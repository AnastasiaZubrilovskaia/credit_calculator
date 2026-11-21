from fastapi.testclient import TestClient


from calculator.app.main import app

client = TestClient(app)

VALID_OFFERS_JSON = {
    "amount": "300000.00",
    "term": 24,
    "firstName": "Ivan",
    "lastName": "Ivanov",
    "middleName": "Ivanovich",
    "email": "ivan@example.com",
    "birthdate": "2001-11-11",
    "passportSeries": "1234",
    "passportNumber": "123456",
}

VALID_CALC_JSON = {
    "amount": "300000.00",
    "term": 24,
    "firstName": "Ivan",
    "lastName": "Ivanov",
    "middleName": "Ivanovich",
    "birthdate": "2001-11-11",
    "passportSeries": "1234",
    "passportNumber": "123456",
    "isInsuranceEnabled": True,
    "isSalaryClient": False,
}


def test_get_offers_success():
    response = client.post("/calculator/offers", json=VALID_OFFERS_JSON)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 4
    first_offer = data[0]
    assert "statementId" in first_offer
    assert "monthlyPayment" in first_offer
    assert "isInsuranceEnabled" in first_offer


def test_get_offers_validation_error():
    bad_json = VALID_OFFERS_JSON.copy()
    bad_json["passportSeries"] = "12"
    response = client.post("/calculator/offers", json=bad_json)
    assert response.status_code == 422


def test_get_offers_age_validation_error():
    bad_json = VALID_OFFERS_JSON.copy()
    bad_json["birthdate"] = "2015-01-01"

    response = client.post("/calculator/offers", json=bad_json)
    assert response.status_code == 422



def test_calculate_credit_success():
    response = client.post("/calculator/calc", json=VALID_CALC_JSON)
    assert response.status_code == 200
    data = response.json()
    assert "monthlyPayment" in data
    assert "psk" in data
    assert "paymentSchedule" in data
    assert len(data["paymentSchedule"]) == 24
    last_payment = data["paymentSchedule"][-1]
    assert last_payment["remainingDebt"] == "0.00"


def test_calculate_credit_validation_error():
    bad_json = VALID_CALC_JSON.copy()
    bad_json["amount"] = "-100000"
    response = client.post("/calculator/calc", json=bad_json)
    assert response.status_code == 422


def test_calculate_credit_amount_validation_error():
    bad_json = VALID_CALC_JSON.copy()
    bad_json["amount"] = "6000000.00"
    response = client.post("/calculator/calc", json=bad_json)
    assert response.status_code == 422