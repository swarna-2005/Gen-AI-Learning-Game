document.addEventListener("DOMContentLoaded", function () {
    const generateQuizBtn = document.getElementById("generateQuiz");
    const quizResultsDiv = document.getElementById("quizResults");
    const quizLoadingDiv = document.getElementById("quizLoading");

    // Event listener for generating quizzes
    generateQuizBtn.addEventListener("click", function () {
        const quizTopic = document.getElementById("quizTopic").value.trim();
        if (!quizTopic) {
            alert("Please enter a topic for the quiz.");
            return;
        }

        quizResultsDiv.innerHTML = "";
        quizLoadingDiv.style.display = "block"; // Show loading spinner

        fetch(`/generate_quiz?topic=${quizTopic}`)
            .then(response => response.json())
            .then(data => {
                quizLoadingDiv.style.display = "none"; // Hide loading spinner
                
                if (!data.questions || data.questions.length === 0) {
                    quizResultsDiv.innerHTML = "<p>No quiz questions found for this topic.</p>";
                    return;
                }

                displayQuiz(data.questions, quizTopic);
            })
            .catch(error => {
                quizLoadingDiv.style.display = "none";
                quizResultsDiv.innerHTML = `<p>Error loading quiz: ${error.message}</p>`;
                console.error("Error fetching quiz:", error);
            });
    });
});

// Function to display quiz questions
function displayQuiz(questions, topic) {
    const quizResultsDiv = document.getElementById("quizResults");
    quizResultsDiv.innerHTML = "<h3>Quiz on " + topic + "</h3>";

    const form = document.createElement("form");
    form.id = "quizForm";

    questions.forEach((question, index) => {
        const questionDiv = document.createElement("div");
        questionDiv.classList.add("quiz-question");

        questionDiv.innerHTML = `
            <p><strong>Q${index + 1}:</strong> ${question.question}</p>
            ${question.options.map((option, i) => `
                <label>
                    <input type="radio" name="q${index}" value="${option}">
                    ${option}
                </label><br>
            `).join("")}
        `;

        form.appendChild(questionDiv);
    });

    const submitBtn = document.createElement("button");
    submitBtn.type = "button";
    submitBtn.textContent = "Submit Quiz";
    submitBtn.classList.add("primary-btn");
    submitBtn.addEventListener("click", () => calculateScore(questions, topic));

    form.appendChild(submitBtn);
    quizResultsDiv.appendChild(form);
}

// Function to calculate quiz score
function calculateScore(questions, topic) {
    let score = 0;
    const totalQuestions = questions.length;

    questions.forEach((question, index) => {
        const selectedAnswer = document.querySelector(`input[name="q${index}"]:checked`);
        if (selectedAnswer && selectedAnswer.value === question.answer) {
            score++;
        }
    });

    const percentageScore = Math.round((score / totalQuestions) * 100);
    displayScore(percentageScore, topic);
}

// Function to display quiz score
function displayScore(score, topic) {
    const quizResultsDiv = document.getElementById("quizResults");
    quizResultsDiv.innerHTML += `
        <div class="quiz-score">
            <h3>Your Score: ${score}%</h3>
        </div>
    `;

    saveQuizScore(topic, score);
}

// Function to save quiz score to backend
function saveQuizScore(subject, score) {
    const userEmail = localStorage.getItem("user_email"); // Assuming login saves user email
    if (!userEmail) {
        alert("Please log in to save scores.");
        return;
    }

    fetch("/save_quiz_score", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: userEmail, subject: subject, score: score })
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            console.log("Score saved successfully!");
            loadAchievements(); // Refresh achievements
        } else {
            console.error("Failed to save score:", data.error);
        }
    })
    .catch(error => console.error("Error saving score:", error));
}
