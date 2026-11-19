// Clinical Client-Side Helper Functions
document.addEventListener('DOMContentLoaded', function () {
    // 1. Automatic BMI Calculation
    const heightInput = document.getElementById('id_height_cm');
    const weightInput = document.getElementById('id_weight_kg');
    const bmiDisplay = document.getElementById('bmi_display');

    function updateBMI() {
        if (!heightInput || !weightInput) return;
        const height = parseFloat(heightInput.value);
        const weight = parseFloat(weightInput.value);

        if (height > 0 && weight > 0) {
            const heightM = height / 100.0;
            const bmi = (weight / (heightM * heightM)).toFixed(2);
            if (bmiDisplay) {
                let badgeClass = 'bg-secondary';
                let category = 'Normal';
                if (bmi < 18.5) { badgeClass = 'bg-warning text-dark'; category = 'Underweight'; }
                else if (bmi < 25.0) { badgeClass = 'bg-success'; category = 'Normal'; }
                else if (bmi < 30.0) { badgeClass = 'bg-warning text-dark'; category = 'Overweight'; }
                else { badgeClass = 'bg-danger'; category = 'Obese'; }

                bmiDisplay.innerHTML = `<span class="badge ${badgeClass} fs-6">${bmi} (${category})</span>`;
            }
        } else {
            if (bmiDisplay) bmiDisplay.innerHTML = '<span class="text-muted">Enter height & weight</span>';
        }
    }

    if (heightInput && weightInput) {
        heightInput.addEventListener('input', updateBMI);
        weightInput.addEventListener('input', updateBMI);
        updateBMI();
    }

    // 2. Pain Scale Slider Label
    const painSlider = document.getElementById('id_pain_score');
    const painLabel = document.getElementById('pain_score_value');
    if (painSlider && painLabel) {
        painSlider.addEventListener('input', function () {
            painLabel.textContent = painSlider.value;
        });
    }

    // 3. Auto-calculate Age from Date of Birth
    const dobInput = document.getElementById('id_date_of_birth');
    const ageInput = document.getElementById('id_age');
    if (dobInput && ageInput) {
        dobInput.addEventListener('change', function () {
            if (this.value) {
                const dob = new Date(this.value);
                const today = new Date();
                let age = today.getFullYear() - dob.getFullYear();
                const m = today.getMonth() - dob.getMonth();
                if (m < 0 || (m === 0 && today.getDate() < dob.getDate())) {
                    age--;
                }
                if (age >= 0) {
                    ageInput.value = age;
                }
            }
        });
    }

    // 4. Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});
