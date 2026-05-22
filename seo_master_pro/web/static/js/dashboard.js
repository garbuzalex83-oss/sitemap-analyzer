// Dashboard JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Анимация круговых диаграмм
    const scoreCircles = document.querySelectorAll('.score-circle');
    
    scoreCircles.forEach(circle => {
        const score = parseInt(circle.getAttribute('data-score'));
        const circlePath = circle.querySelector('.circle');
        
        if (circlePath) {
            // Анимация при загрузке
            setTimeout(() => {
                circlePath.style.strokeDasharray = `${score}, 100`;
            }, 500);
        }
    });
    
    // Плавная прокрутка для навигации
    document.querySelectorAll('.nav-item[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            const target = document.querySelector(targetId);
            
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
                
                // Обновляем активный класс
                document.querySelectorAll('.nav-item').forEach(item => {
                    item.classList.remove('active');
                });
                this.classList.add('active');
            }
        });
    });
    
    // Подсветка активного раздела при скролле
    const sections = document.querySelectorAll('.audit-section, .score-section');
    const navItems = document.querySelectorAll('.sidebar-nav .nav-item');
    
    window.addEventListener('scroll', () => {
        let current = '';
        
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.clientHeight;
            
            if (window.scrollY >= sectionTop - 200) {
                current = section.getAttribute('id');
            }
        });
        
        navItems.forEach(item => {
            item.classList.remove('active');
            if (item.getAttribute('href') === `#${current}`) {
                item.classList.add('active');
            }
        });
    });
    
    // Анимация появления элементов
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
    
    // Наблюдаем за карточками
    document.querySelectorAll('.score-card, .stat-box, .factor-item').forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        observer.observe(card);
    });
    
    // Тултипы для метрик
    document.querySelectorAll('.stat-box').forEach(stat => {
        stat.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.transition = 'transform 0.3s ease';
        });
        
        stat.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
    
    // Кнопка печати
    const printButton = document.querySelector('button[onclick="window.print()"]');
    if (printButton) {
        printButton.addEventListener('click', function() {
            setTimeout(() => {
                alert('Совет: Для сохранения в PDF выберите "Сохранить как PDF" в диалоге печати.');
            }, 1000);
        });
    }
    
    // Динамическое обновление времени
    const auditDateElement = document.querySelector('.audit-date');
    if (auditDateElement) {
        const dateString = auditDateElement.textContent.trim();
        const date = new Date(dateString);
        
        // Форматируем дату
        const formattedDate = new Intl.DateTimeFormat('ru-RU', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        }).format(date);
        
        auditDateElement.textContent = formattedDate;
    }
});

// Утилиты для цветовых индикаторов
function getScoreColor(score) {
    if (score >= 90) return '#10b981';
    if (score >= 75) return '#3b82f6';
    if (score >= 50) return '#f59e0b';
    return '#ef4444';
}

function getScoreLabel(score) {
    if (score >= 90) return 'Отлично';
    if (score >= 75) return 'Хорошо';
    if (score >= 50) return 'Требует доработки';
    return 'Критично';
}

// Экспорт данных в CSV
function exportToCSV(data, filename) {
    const csvContent = "data:text/csv;charset=utf-8," + data.map(row => row.join(',')).join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", filename);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}
