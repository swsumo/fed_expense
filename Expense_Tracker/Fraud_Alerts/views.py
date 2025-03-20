from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse

@login_required  # Restrict access to logged-in users
def fraud_alerts_view(request):
    return render(request, "Fraud_Alerts/fraud_index.html")

def predict_fraud(request):
    if request.method == "POST":
        amount = float(request.POST.get("amount"))
        category = request.POST.get("category")

        # Dummy logic: If amount > 1000, assume fraudulent, otherwise legit
        result = "Fraudulent" if amount > 1000 else "Legit"

        return JsonResponse({"result": result})  

    return JsonResponse({"error": "Invalid request"}, status=400)

#imrpove this acc to the model