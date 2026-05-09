/* ═══════════════════════════════════════════════════
   İnme Risk Sistemi — Application Logic
   ═══════════════════════════════════════════════════ */

// ── LocalStorage Database Helpers ──
const DB_KEY = 'inmeRiskDoctors';

function getDB() {
    const raw = localStorage.getItem(DB_KEY);
    return raw ? JSON.parse(raw) : [];
}

function saveDB(doctors) {
    localStorage.setItem(DB_KEY, JSON.stringify(doctors));
}

function generateDoctorId() {
    const doctors = getDB();
    const nextNum = doctors.length + 1;
    return 'DR-' + String(nextNum).padStart(5, '0');
}

function formatDate(date) {
    const d = new Date(date);
    const day = String(d.getDate()).padStart(2, '0');
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const year = d.getFullYear();
    return `${day}.${month}.${year}`;
}

function formatDateTime(date) {
    const d = new Date(date);
    const day = String(d.getDate()).padStart(2, '0');
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const year = d.getFullYear();
    const hour = String(d.getHours()).padStart(2, '0');
    const min = String(d.getMinutes()).padStart(2, '0');
    return `${day}.${month}.${year} ${hour}:${min}`;
}

function maskTC(tc) {
    if (!tc || tc.length < 4) return tc;
    return tc.substring(0, 3) + '•••' + tc.substring(tc.length - 3);
}

const SECURITY_QUESTIONS = {
    anne: 'Annenizin kızlık soyadı nedir?',
    okul: 'İlkokul adınız nedir?',
    sehir: 'Doğduğunuz şehir neresidir?',
    hayvan: 'İlk evcil hayvanınızın adı nedir?'
};

// ── Toast System ──
function showToast(message, type = 'info', duration = 3500) {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;

    const icons = { success: '✅', error: '❌', info: 'ℹ️', warning: '⚠️' };
    toast.innerHTML = `
        <span class="toast-icon">${icons[type] || icons.info}</span>
        <span>${message}</span>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('toast-exit');
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

// ── Screen Navigation ──
let currentScreen = 'screenLogin';
let loggedInDoctor = null;

function showScreen(screenId) {
    document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
    setTimeout(() => {
        document.getElementById(screenId).classList.add('active');
        currentScreen = screenId;
    }, 50);
}

// ── Validation Helpers ──
function isValidTC(tc) {
    return /^\d{11}$/.test(tc);
}

function shakeElement(el) {
    el.classList.add('shake');
    setTimeout(() => el.classList.remove('shake'), 500);
}

function setInputError(inputId) {
    const wrapper = document.getElementById(inputId).closest('.input-wrapper');
    wrapper.classList.add('error');
    shakeElement(wrapper);
    setTimeout(() => wrapper.classList.remove('error'), 2000);
}

// ── Background Particles ──
function createParticles() {
    const container = document.getElementById('bgParticles');
    const count = 25;
    for (let i = 0; i < count; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        const size = Math.random() * 4 + 1;
        particle.style.width = size + 'px';
        particle.style.height = size + 'px';
        particle.style.left = Math.random() * 100 + '%';
        particle.style.animationDuration = (Math.random() * 15 + 10) + 's';
        particle.style.animationDelay = (Math.random() * 10) + 's';
        particle.style.opacity = Math.random() * 0.4 + 0.1;
        container.appendChild(particle);
    }
}

// ═══════════════════════════════════════════
// EVENT HANDLERS
// ═══════════════════════════════════════════

document.addEventListener('DOMContentLoaded', () => {
    createParticles();

    // ── Toggle Password Visibility ──
    document.querySelectorAll('.toggle-password').forEach(btn => {
        btn.addEventListener('click', () => {
            const targetId = btn.getAttribute('data-target');
            const input = document.getElementById(targetId);
            if (input.type === 'password') {
                input.type = 'text';
                btn.querySelector('.eye-icon').textContent = '🙈';
            } else {
                input.type = 'password';
                btn.querySelector('.eye-icon').textContent = '👁️';
            }
        });
    });

    // ── SCREEN 1: Login ──
    document.getElementById('loginForm').addEventListener('submit', (e) => {
        e.preventDefault();

        const tc = document.getElementById('loginTC').value.trim();
        const password = document.getElementById('loginPassword').value;

        if (!isValidTC(tc)) {
            setInputError('loginTC');
            showToast('TC Kimlik Numarası 11 haneli olmalıdır.', 'error');
            return;
        }

        const doctors = getDB();
        const doctor = doctors.find(d => d.tc === tc);

        if (!doctor) {
            setInputError('loginTC');
            showToast('Bu TC ile kayıtlı doktor bulunamadı.', 'error');
            return;
        }

        if (doctor.password !== password) {
            setInputError('loginPassword');
            showToast('Şifre hatalı. Lütfen tekrar deneyin.', 'error');
            return;
        }

        // Login successful
        doctor.lastLogin = new Date().toISOString();
        saveDB(doctors);
        loggedInDoctor = doctor;

        showToast(`Hoş geldiniz, Dr. ${doctor.name} ${doctor.surname}!`, 'success');
        populateProfile(doctor);
        
        // Show loading on button briefly
        const btn = document.getElementById('btnLogin');
        const loader = btn.querySelector('.btn-loader');
        const spans = btn.querySelectorAll('span');
        spans.forEach(s => s.style.display = 'none');
        loader.style.display = 'block';

        setTimeout(() => {
            spans.forEach(s => s.style.display = '');
            loader.style.display = 'none';
            showScreen('screenProfile');
        }, 800);
    });

    // ── Navigate to Register ──
    document.getElementById('btnGoRegister').addEventListener('click', () => {
        showScreen('screenRegister');
    });

    // ── Navigate to Forgot Password ──
    document.getElementById('btnGoForgot').addEventListener('click', () => {
        document.getElementById('forgotStep1').classList.remove('hidden');
        document.getElementById('forgotStep2').classList.add('hidden');
        showScreen('screenForgot');
    });

    // ── Back to Login buttons ──
    document.getElementById('btnBackToLogin1').addEventListener('click', () => showScreen('screenLogin'));
    document.getElementById('btnBackToLogin2').addEventListener('click', () => showScreen('screenLogin'));

    // ── SCREEN 2: Register ──
    document.getElementById('registerForm').addEventListener('submit', (e) => {
        e.preventDefault();

        const tc = document.getElementById('regTC').value.trim();
        const name = document.getElementById('regName').value.trim();
        const surname = document.getElementById('regSurname').value.trim();
        const specialty = document.getElementById('regSpecialty').value;
        const password = document.getElementById('regPassword').value;
        const passwordConfirm = document.getElementById('regPasswordConfirm').value;
        const securityQ = document.getElementById('regSecurityQ').value;
        const securityA = document.getElementById('regSecurityA').value.trim();

        // Validations
        if (!isValidTC(tc)) {
            setInputError('regTC');
            showToast('TC Kimlik Numarası 11 haneli olmalıdır.', 'error');
            return;
        }

        const doctors = getDB();
        if (doctors.find(d => d.tc === tc)) {
            setInputError('regTC');
            showToast('Bu TC ile zaten bir hesap mevcut.', 'error');
            return;
        }

        if (!name || !surname) {
            showToast('Ad ve soyad alanları zorunludur.', 'error');
            return;
        }

        if (!specialty) {
            showToast('Lütfen uzmanlık alanınızı seçin.', 'error');
            return;
        }

        if (password.length < 6) {
            setInputError('regPassword');
            showToast('Şifre en az 6 karakter olmalıdır.', 'error');
            return;
        }

        if (password !== passwordConfirm) {
            setInputError('regPasswordConfirm');
            showToast('Şifreler eşleşmiyor.', 'error');
            return;
        }

        if (!securityQ || !securityA) {
            showToast('Güvenlik sorusu ve cevabı zorunludur.', 'error');
            return;
        }

        // Create doctor
        const newDoctor = {
            id: generateDoctorId(),
            tc,
            name,
            surname,
            specialty,
            password,
            securityQ,
            securityA: securityA.toLowerCase(),
            registeredAt: new Date().toISOString(),
            lastLogin: null
        };

        doctors.push(newDoctor);
        saveDB(doctors);

        showToast(`Hesabınız oluşturuldu! Doktor ID: ${newDoctor.id}`, 'success', 4000);

        // Clear form
        document.getElementById('registerForm').reset();

        setTimeout(() => showScreen('screenLogin'), 1200);
    });

    // ── SCREEN 3: Forgot Password ──
    let forgotTargetDoctor = null;

    // Step 1
    document.getElementById('btnForgotStep1').addEventListener('click', () => {
        const tc = document.getElementById('forgotTC').value.trim();

        if (!isValidTC(tc)) {
            setInputError('forgotTC');
            showToast('TC Kimlik Numarası 11 haneli olmalıdır.', 'error');
            return;
        }

        const doctors = getDB();
        const doctor = doctors.find(d => d.tc === tc);

        if (!doctor) {
            setInputError('forgotTC');
            showToast('Bu TC ile kayıtlı doktor bulunamadı.', 'error');
            return;
        }

        forgotTargetDoctor = doctor;

        // Show security question
        const questionText = SECURITY_QUESTIONS[doctor.securityQ] || 'Güvenlik sorusu bulunamadı';
        document.getElementById('securityQuestionDisplay').innerHTML = `
            <div class="sq-label">Güvenlik Sorunuz</div>
            <div class="sq-text">${questionText}</div>
        `;

        // Go to step 2
        document.getElementById('forgotStep1').classList.add('hidden');
        document.getElementById('forgotStep2').classList.remove('hidden');
    });

    // Back to step 1
    document.getElementById('btnBackToStep1').addEventListener('click', () => {
        document.getElementById('forgotStep2').classList.add('hidden');
        document.getElementById('forgotStep1').classList.remove('hidden');
        forgotTargetDoctor = null;
    });

    // Step 2 — Reset Password
    document.getElementById('btnResetPassword').addEventListener('click', () => {
        const answer = document.getElementById('forgotSecurityA').value.trim();
        const newPass = document.getElementById('forgotNewPass').value;
        const newPassConfirm = document.getElementById('forgotNewPassConfirm').value;

        if (!answer) {
            setInputError('forgotSecurityA');
            showToast('Lütfen güvenlik sorusunu cevaplayın.', 'error');
            return;
        }

        if (answer.toLowerCase() !== forgotTargetDoctor.securityA) {
            setInputError('forgotSecurityA');
            showToast('Güvenlik sorusu cevabı hatalı.', 'error');
            return;
        }

        if (newPass.length < 6) {
            setInputError('forgotNewPass');
            showToast('Yeni şifre en az 6 karakter olmalıdır.', 'error');
            return;
        }

        if (newPass !== newPassConfirm) {
            setInputError('forgotNewPassConfirm');
            showToast('Şifreler eşleşmiyor.', 'error');
            return;
        }

        // Update password
        const doctors = getDB();
        const idx = doctors.findIndex(d => d.tc === forgotTargetDoctor.tc);
        doctors[idx].password = newPass;
        saveDB(doctors);

        showToast('Şifreniz başarıyla güncellendi! Giriş yapabilirsiniz.', 'success', 4000);

        // Clear fields
        document.getElementById('forgotSecurityA').value = '';
        document.getElementById('forgotNewPass').value = '';
        document.getElementById('forgotNewPassConfirm').value = '';
        forgotTargetDoctor = null;

        setTimeout(() => showScreen('screenLogin'), 1500);
    });

    // ── SCREEN 4: Profile ──

    // Toggle change password section
    document.getElementById('btnToggleChangePass').addEventListener('click', () => {
        const content = document.getElementById('changePassSection');
        const toggle = document.getElementById('btnToggleChangePass');
        content.classList.toggle('hidden');
        toggle.classList.toggle('open');
    });

    // Change Password
    document.getElementById('btnChangePass').addEventListener('click', () => {
        const currentPass = document.getElementById('currentPass').value;
        const newPass = document.getElementById('newPass').value;
        const newPassConfirm = document.getElementById('newPassConfirm').value;

        if (!currentPass) {
            setInputError('currentPass');
            showToast('Mevcut şifrenizi girin.', 'error');
            return;
        }

        if (currentPass !== loggedInDoctor.password) {
            setInputError('currentPass');
            showToast('Mevcut şifre hatalı.', 'error');
            return;
        }

        if (newPass.length < 6) {
            setInputError('newPass');
            showToast('Yeni şifre en az 6 karakter olmalıdır.', 'error');
            return;
        }

        if (newPass !== newPassConfirm) {
            setInputError('newPassConfirm');
            showToast('Yeni şifreler eşleşmiyor.', 'error');
            return;
        }

        // Update
        const doctors = getDB();
        const idx = doctors.findIndex(d => d.tc === loggedInDoctor.tc);
        doctors[idx].password = newPass;
        loggedInDoctor.password = newPass;
        saveDB(doctors);

        showToast('Şifreniz başarıyla değiştirildi!', 'success');

        // Clear and collapse
        document.getElementById('currentPass').value = '';
        document.getElementById('newPass').value = '';
        document.getElementById('newPassConfirm').value = '';
        document.getElementById('changePassSection').classList.add('hidden');
        document.getElementById('btnToggleChangePass').classList.remove('open');
    });

    // Go to Patient Module (placeholder)
    document.getElementById('btnGoPatient').addEventListener('click', () => {
        showToast('Hasta Modülüne yönlendiriliyorsunuz...', 'info');
        // TODO: Navigate to patient module
    });

    // Logout
    document.getElementById('btnLogout').addEventListener('click', () => {
        loggedInDoctor = null;
        document.getElementById('loginForm').reset();
        showToast('Güvenli çıkış yapıldı.', 'info');
        showScreen('screenLogin');
    });
});

// ── Populate Profile Data ──
function populateProfile(doctor) {
    document.getElementById('profileName').textContent = `Dr. ${doctor.name} ${doctor.surname}`;
    document.getElementById('profileSpecialtyBadge').textContent = doctor.specialty;
    document.getElementById('profileDoctorId').textContent = doctor.id;
    document.getElementById('profileTC').textContent = maskTC(doctor.tc);
    document.getElementById('profileSpecialty').textContent = doctor.specialty;
    document.getElementById('profileRegDate').textContent = formatDate(doctor.registeredAt);
    document.getElementById('profileLastLogin').textContent = doctor.lastLogin ? formatDateTime(doctor.lastLogin) : 'İlk giriş';

    // Set avatar based on name
    const firstChar = doctor.name.charAt(0).toUpperCase();
    // Random gender icon based on name variety
    document.getElementById('profileAvatar').innerHTML = `<span>👨‍⚕️</span>`;
}
