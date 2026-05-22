// SEO Master PRO - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const auditForm = document.getElementById('auditForm');
    const progressContainer = document.getElementById('progressContainer');
    const progressBar = document.getElementById('progressBar');
    const progressPercent = document.getElementById('progressPercent');
    const steps = document.querySelectorAll('.step');
    
    if (auditForm) {
        auditForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            // Получаем данные формы
            const formData = new FormData(auditForm);
            const url = formData.get('url');
            
            if (!url) {
                alert('Пожалуйста, введите URL сайта');
                return;
            }
            
            // Показываем прогресс
            progressContainer.style.display = 'block';
            progressBar.style.width = '0%';
            progressPercent.textContent = '0%';
            
            // Сбрасываем шаги
            steps.forEach(step => {
                step.classList.remove('active', 'completed');
            });
            
            try {
                // Отправляем запрос на аудит
                const response = await fetch('/api/audit/start', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                if (result.success) {
                    // Обновляем прогресс
                    updateProgress(100);
                    
                    // Показываем сообщение об успехе
                    setTimeout(() => {
                        alert(`✅ Аудит успешно завершен!\n\nОбщая оценка: ${result.scores.overall}/100\n\nТехнический SEO: ${result.scores.technical}/100\nOn-Page: ${result.scores.onpage}/100\nКоммерческие факторы: ${result.scores.commercial}/100\nJS Рендеринг: ${result.scores.js}/100\n\nПеренаправление на дашборд...`);
                        
                        // Перенаправляем на дашборд
                        window.location.href = `/dashboard/${result.audit_id}`;
                    }, 1000);
                } else {
                    throw new Error(result.error || 'Ошибка при выполнении аудита');
                }
                
            } catch (error) {
                console.error('Audit error:', error);
                alert(`❌ Ошибка: ${error.message}`);
                progressContainer.style.display = 'none';
            }
        });
    }
    
    // Функция обновления прогресса
    function updateProgress(percent) {
        progressBar.style.width = `${percent}%`;
        progressPercent.textContent = `${percent}%`;
        
        // Обновляем шаги
        const totalSteps = steps.length;
        const currentStep = Math.floor((percent / 100) * totalSteps);
        
        steps.forEach((step, index) => {
            step.classList.remove('active', 'completed');
            
            if (index < currentStep) {
                step.classList.add('completed');
            } else if (index === currentStep && percent < 100) {
                step.classList.add('active');
            }
        });
    }
    
    // Плавная прокрутка для якорных ссылок
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href !== '#') {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });
    
    // Анимация появления элементов при скролле
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);
    
    // Наблюдаем за карточками функций
    document.querySelectorAll('.feature-card').forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(card);
    });
});

// Дополнительные утилиты
function formatNumber(num) {
    return new Intl.NumberFormat('ru-RU').format(num);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('ru-RU', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    }).format(date);
}

function getScoreColor(score) {
    if (score >= 90) return '#10b981'; // Green
    if (score >= 75) return '#3b82f6'; // Blue
    if (score >= 50) return '#f59e0b'; // Orange
    return '#ef4444'; // Red
}

function getScoreLabel(score) {
    if (score >= 90) return 'Отлично';
    if (score >= 75) return 'Хорошо';
    if (score >= 50) return 'Требует доработки';
    return 'Критично';
}
