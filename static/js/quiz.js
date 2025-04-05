document.addEventListener('DOMContentLoaded', function() {
    const generateBtn = document.getElementById('generateQuiz');
    const quizTopic = document.getElementById('quizTopic');
    const quizResults = document.getElementById('quizResults');
    const quizLoading = document.getElementById('quizLoading');

    generateBtn.addEventListener('click', function() {
        const topic = quizTopic.value.trim();
        if (!topic) {
            alert('Please enter a quiz topic');
            return;
        }

        quizLoading.style.display = 'block';
        quizResults.innerHTML = '';

        // Call your Flask backend to generate quiz
        fetch('/generate_quiz', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ topic: topic })
        })
        .then(response => response.json())
        .then(data => {
            quizLoading.style.display = 'none';
            if (data.error) {
                quizResults.innerHTML = `<div class="error-message">${data.error}</div>`;
                return;
            }
            
            displayQuiz(data.quiz);
        })
        .catch(error => {
            quizLoading.style.display = 'none';
            quizResults.innerHTML = `<div class="error-message">Error generating quiz: ${error.message}</div>`;
        });
    });

    function displayQuiz(quiz) {
        let html = `<h3>Quiz on ${quiz[0].topic}</h3>`;
        
        quiz.forEach((q, index) => {
            html += `
            <div class="quiz-item">
                <p><strong>Q${index + 1}:</strong> ${q.question}</p>
                <div class="quiz-options">
                    <div class="quiz-option" data-correct="${q.correct_answer === 'A'}">A: ${q.option_a}</div>
                    <div class="quiz-option" data-correct="${q.correct_answer === 'B'}">B: ${q.option_b}</div>
                    <div class="quiz-option" data-correct="${q.correct_answer === 'C'}">C: ${q.option_c}</div>
                    <div class="quiz-option" data-correct="${q.correct_answer === 'D'}">D: ${q.option_d}</div>
                </div>
            </div>
            `;
        });

        quizResults.innerHTML = html;

        // Add click handlers for quiz options
        document.querySelectorAll('.quiz-option').forEach(option => {
            option.addEventListener('click', function() {
                const isCorrect = this.getAttribute('data-correct') === 'true';
                this.style.backgroundColor = isCorrect ? '#d4edda' : '#f8d7da';
                this.style.borderColor = isCorrect ? '#c3e6cb' : '#f5c6cb';
            });
        });
    }
});