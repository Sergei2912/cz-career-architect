from app.services.text_analysis import analyze_text


def test_analyze_text_no_issues():
    text = "Full Name, +420 123 456 789, email@example.com"
    issues = analyze_text(text)
    assert len(issues) == 0


def test_analyze_text_with_birth_date():
    text = "Date of birth 1.1.1990"
    issues = analyze_text(text)
    assert any("дата рождения" in i for i in issues)


def test_analyze_text_with_bad_date_format():
    text = "Date: 15.01.2025"
    issues = analyze_text(text)
    assert any("Формат даты" in i for i in issues)
