from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q
from django.utils import timezone 
from django.contrib.auth.models import User 
from django.urls import reverse
from .models import ExpenseGroup, GroupExpense, ExpenseSplit, DebtSettlement
from .forms import ExpenseGroupForm, GroupExpenseForm, AddMemberForm, DebtSettlementForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
# from .models import Group



def group_management(request):
    return render(request, 'shared_expenses/group_management.html')

@login_required
def dashboard(request):
    """Dashboard view showing summary of all groups and expenses"""
    user_groups = ExpenseGroup.objects.filter(members=request.user)
    expenses = GroupExpense.objects.filter(group__in=user_groups).order_by('-date')[:5]
    
    # Calculate total balances
    total_owed = ExpenseSplit.objects.filter(
        user=request.user,
        is_settled=False
    ).aggregate(Sum('amount_owed'))['amount_owed__sum'] or 0
    
    total_owed_to_you = ExpenseSplit.objects.filter(
        expense__payer=request.user,
        is_settled=False
    ).exclude(user=request.user).aggregate(Sum('amount_owed'))['amount_owed__sum'] or 0

    return render(request, 'shared_expenses/group_management.html', {
        'active_section': 'dashboard',
        'user_groups': user_groups,
        'recent_expenses': expenses,
        'total_owed': total_owed,
        'total_owed_to_you': total_owed_to_you,
    })



@login_required
def your_view(request):
    if request.method == 'POST' and 'group_name' in request.POST:
        try:
            group = ExpenseGroup.objects.create(  # Changed from Group to ExpenseGroup
                name=request.POST['group_name'],
                description=request.POST.get('group_description', ''),
                admin=request.user
            )
            group.members.add(request.user)  # Add creator as member
            messages.success(request, 'Group created successfully!')
            return redirect(request.path)
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    context = {
        # Changed from Group to ExpenseGroup
        'user_groups': ExpenseGroup.objects.filter(members=request.user),
    }
    return render(request, 'your_template.html', context)

@csrf_exempt  # Temporary to bypass CSRF for testing
def create_group(request):
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            description = request.POST.get('description', '')
            
            # Create the group (adjust according to your model)
            group = Group.objects.create(
                name=name,
                description=description,
                admin=request.user
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Group created successfully',
                'group_id': group.id
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)
    
    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)


@login_required
def delete_group(request, group_id):
    """
    Allow only admins to delete the group
    """
    group = get_object_or_404(ExpenseGroup, id=group_id)

    if request.user != group.admin:
        messages.error(request, "Only the group admin can delete this group.")
        return redirect('manage_groups')

    if request.method == 'POST':
        group_name = group.name
        group.delete()
        messages.success(request, f"Group '{group_name}' deleted successfully!")
        return redirect('manage_groups')
    
    return render(request, 'shared_expenses/group_management.html', {
        'active_section': 'confirm_delete',
        'object': group,
        'object_type': 'group'
    })

@login_required
def join_group(request, group_id):
    """
    Join an existing group
    """
    group = get_object_or_404(ExpenseGroup, id=group_id)
    
    if request.user in group.members.all():
        messages.warning(request, "You're already a member of this group.")
    else:
        group.members.add(request.user)
        messages.success(request, f"You've successfully joined {group.name}!")
    
    return redirect('group_detail', group_id=group.id)

@login_required
def manage_groups(request):
    """View for managing groups and creating new ones"""
    group_form = ExpenseGroupForm(request.POST or None, user=request.user)
    
    if request.method == "POST" and group_form.is_valid():
        group = group_form.save(commit=False)
        group.admin = request.user
        group.save()
        group.members.add(request.user)  # Add admin as member
        
        # Add selected members
        members = group_form.cleaned_data.get('members', [])
        group.members.add(*members)
        
        messages.success(request, f"Group '{group.name}' created successfully!")
        return redirect('manage_groups')

    user_groups = ExpenseGroup.objects.filter(members=request.user)
    return render(request, 'shared_expenses/group_management.html', {
        'active_section': 'groups',
        'group_form': group_form,
        'user_groups': user_groups,
    })

@login_required
def group_detail(request, group_id):
    """Detailed view of a specific group"""
    group = get_object_or_404(ExpenseGroup, id=group_id, members=request.user)
    expenses = group.expenses.all().order_by('-date')
    members = group.members.all()
    
    # Calculate balances for each member
    balances = {}
    for member in members:
        total_paid = group.expenses.filter(payer=member).aggregate(Sum('amount'))['amount__sum'] or 0
        total_owed = ExpenseSplit.objects.filter(
            user=member,
            expense__group=group
        ).aggregate(Sum('amount_owed'))['amount_owed__sum'] or 0
        balances[member] = total_paid - total_owed
    
    # Calculate debt transactions
    debt_transactions = calculate_debt_transactions(group)
    
    return render(request, 'shared_expenses/group_management.html', {
        'active_section': 'group_detail',
        'group': group,
        'expenses': expenses,
        'members': members,
        'balances': balances,
        'debt_transactions': debt_transactions,
    })

@login_required
def add_member(request, group_id):
    """Add a member to a group"""
    group = get_object_or_404(ExpenseGroup, id=group_id, admin=request.user)
    
    if request.method == "POST":
        form = AddMemberForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                if user not in group.members.all():
                    group.members.add(user)
                    messages.success(request, f"{user.username} added to the group!")
                else:
                    messages.warning(request, "User is already a member of this group.")
                return redirect('group_detail', group_id=group.id)
            except User.DoesNotExist:
                messages.error(request, "User with this email does not exist.")
    else:
        form = AddMemberForm()
    
    return render(request, 'shared_expenses/group_management.html', {
        'active_section': 'add_member',
        'form': form,
        'group': group,
    })


@login_required
def add_expense(request, group_id):
    if request.method == "POST":
        form = GroupExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.group_id = group_id
            expense.payer = request.user
            expense.save()
            
            # Split logic here...
            
            return JsonResponse({
                'success': True,
                'message': 'Expense added successfully!',
                'expense_id': expense.id
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def edit_expense(request, expense_id):
    """
    Allow only the payer to edit an expense
    """
    expense = get_object_or_404(GroupExpense, id=expense_id)
    
    # Verify the current user is the payer
    if request.user != expense.payer:
        messages.error(request, "Only the payer can edit this expense.")
        return redirect('group_detail', group_id=expense.group.id)

    if request.method == 'POST':
        form = GroupExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            messages.success(request, "Expense updated successfully!")
            return redirect('group_detail', group_id=expense.group.id)
    else:
        form = GroupExpenseForm(instance=expense)
    
    return render(request, 'shared_expenses/group_management.html', {
        'active_section': 'edit_expense',
        'form': form,
        'expense': expense
    })

@login_required
def delete_expense(request, expense_id):
    """
    Allow only the payer to delete an expense
    """
    expense = get_object_or_404(GroupExpense, id=expense_id)
    
    # Verify the current user is the payer
    if request.user != expense.payer:
        messages.error(request, "Only the payer can delete this expense.")
        return redirect('group_detail', group_id=expense.group.id)

    if request.method == 'POST':
        group_id = expense.group.id
        expense.delete()
        messages.success(request, "Expense deleted successfully!")
        return redirect('group_detail', group_id=group_id)
    
    return render(request, 'shared_expenses/group_management.html', {
        'active_section': 'confirm_delete',
        'object': expense,
        'object_type': 'expense',
        'cancel_url': reverse('group_detail', kwargs={'group_id': expense.group.id})
    })

@login_required
def verify_settlement(request, settlement_id):
    """
    Allow creditor to verify a debt settlement
    """
    settlement = get_object_or_404(DebtSettlement, id=settlement_id)
    
    # Verify current user is the creditor
    if request.user != settlement.creditor:
        messages.error(request, "Only the creditor can verify this settlement.")
        return redirect('group_detail', group_id=settlement.group.id)

    if request.method == 'POST':
        settlement.is_verified = True
        settlement.save()
        
        # Mark related expense splits as settled
        ExpenseSplit.objects.filter(
            expense__group=settlement.group,
            expense__payer=settlement.creditor,
            user=settlement.debtor,
            is_settled=False
        ).update(
            is_settled=True,
            settled_at=timezone.now()
        )
        
        messages.success(request, "Settlement verified successfully!")
        return redirect('group_detail', group_id=settlement.group.id)
    
    return render(request, 'shared_expenses/group_management.html', {
        'active_section': 'verify_settlement',
        'settlement': settlement
    })

@login_required
def settle_debt(request, group_id):
    """Settle debts between group members"""
    group = get_object_or_404(ExpenseGroup, id=group_id, members=request.user)
    
    if request.method == "POST":
        form = DebtSettlementForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            creditor = request.user
            
            # Find a debtor who owes this user
            debtor = None
            debt_transactions = calculate_debt_transactions(group)
            for debtor_user, creditor_user, amt in debt_transactions:
                if creditor_user == request.user:
                    debtor = debtor_user
                    break
            
            if debtor:
                # Create settlement record
                DebtSettlement.objects.create(
                    group=group,
                    debtor=debtor,
                    creditor=creditor,
                    amount=amount
                )
                
                # Mark relevant splits as settled
                splits = ExpenseSplit.objects.filter(
                    expense__group=group,
                    user=debtor,
                    expense__payer=creditor,
                    is_settled=False
                ).order_by('expense__date')
                
                remaining = amount
                for split in splits:
                    if remaining <= 0:
                        break
                    if split.amount_owed <= remaining:
                        split.is_settled = True
                        split.settled_at = timezone.now()
                        split.save()
                        remaining -= split.amount_owed
                    else:
                        # Create a new split for partial payment
                        new_split = ExpenseSplit.objects.create(
                            expense=split.expense,
                            user=split.user,
                            amount_owed=split.amount_owed - remaining,
                            is_settled=False
                        )
                        split.amount_owed = remaining
                        split.is_settled = True
                        split.settled_at = timezone.now()
                        split.save()
                        remaining = 0
                
                messages.success(request, f"Debt settlement of ${amount} recorded!")
                return redirect('group_detail', group_id=group.id)
            else:
                messages.error(request, "No debts to settle with this user.")
    else:
        form = DebtSettlementForm()
    
    return render(request, 'shared_expenses/group_management.html', {
        'active_section': 'settle_debt',
        'form': form,
        'group': group,
    })

def calculate_debt_transactions(group):
    """Helper function to calculate debt transactions for a group"""
    members = group.members.all()
    balances = {}

    # Calculate balances for each member
    for member in members:
        total_paid = group.expenses.filter(payer=member).aggregate(Sum('amount'))['amount__sum'] or 0
        total_owed = ExpenseSplit.objects.filter(
            user=member,
            expense__group=group,
            is_settled=False
        ).aggregate(Sum('amount_owed'))['amount_owed__sum'] or 0
        balances[member] = total_paid - total_owed

    # Separate creditors and debtors
    creditors = sorted(
        [(user, balance) for user, balance in balances.items() if balance > 0],
        key=lambda x: -x[1]
    )
    debtors = sorted(
        [(user, balance) for user, balance in balances.items() if balance < 0],
        key=lambda x: x[1]
    )

    # Calculate transactions
    transactions = []
    while creditors and debtors:
        creditor, credit_amount = creditors[0]
        debtor, debt_amount = debtors[0]
        
        settlement_amount = min(credit_amount, -debt_amount)
        transactions.append((debtor, creditor, settlement_amount, group))
        
        # Update balances
        if credit_amount == settlement_amount:
            creditors.pop(0)
        else:
            creditors[0] = (creditor, credit_amount - settlement_amount)
        
        if -debt_amount == settlement_amount:
            debtors.pop(0)
        else:
            debtors[0] = (debtor, debt_amount + settlement_amount)
    
    return transactions