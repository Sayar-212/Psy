class PsyGenAssessment {
    constructor() {
        this.currentQuestion = 0;
        this.responses = [];
        this.scores = [];
        this.isIntroComplete = false;
        this.awaitingResponse = false;
        this.conversationStarted = false;
        
        this.questions = [
            { id: 1, text: "How have you been feeling emotionally lately?", category: "sadness", source: "BDI" },
            { id: 2, text: "Tell me about your outlook on the future. How do you see things unfolding?", category: "hopelessness", source: "BDI" },
            { id: 3, text: "How satisfied do you feel with the things you usually enjoy?", category: "satisfaction", source: "BDI" },
            { id: 4, text: "How has your sleep been recently?", category: "sleep", source: "BDI" },
            { id: 5, text: "What's your energy level like these days?", category: "energy", source: "BDI" },
            { id: 6, text: "How do you feel about yourself when you look in the mirror or think about who you are?", category: "self_worth", source: "BDI" },
            { id: 7, text: "How easy or difficult is it for you to make decisions lately?", category: "decision_making", source: "BDI" },
            { id: 8, text: "Over the past two weeks, how often have you felt down, depressed, or hopeless?", category: "depression_frequency", source: "PHQ" },
            { id: 9, text: "How much interest or pleasure have you had in doing things you normally enjoy?", category: "interest", source: "PHQ" },
            { id: 10, text: "Have you had any thoughts that you'd be better off not being here, or thoughts of hurting yourself?", category: "suicidal_ideation", source: "PHQ" }
        ];
        
        this.init();
        this.preventScreenshots();
    }
    
    init() {
        this.introContainer = document.getElementById('introContainer');
        this.chatContainer = document.getElementById('chatContainer');
        this.chatMessages = document.getElementById('chatMessages');
        this.userInput = document.getElementById('userInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.bgMusic = document.getElementById('bgMusic');
        
        // Don't auto-start animation, wait for disclaimer acceptance
        
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        this.userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendMessage();
        });
    }
    
    preventScreenshots() {
        let blurTimeout;
        
        document.addEventListener('keyup', (e) => {
            if (e.key == 'PrintScreen') {
                navigator.clipboard.writeText('');
                this.terminateSession();
            }
        });
        
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && (e.key === 'p' || e.key === 's' || e.key === 'c')) {
                e.preventDefault();
                return false;
            }
        });
        
        window.addEventListener('blur', () => {
            blurTimeout = setTimeout(() => {
                this.terminateSession();
            }, 2000);
        });
        
        window.addEventListener('focus', () => {
            clearTimeout(blurTimeout);
        });
        
        window.confirmTermination = () => {
            localStorage.clear();
            sessionStorage.clear();
            window.location.href = 'index.html';
        };
    }
    
    terminateSession() {
        document.getElementById('terminationOverlay').classList.add('active');
    }
    
    startIntroAnimation() {
        // Only start if disclaimer is accepted (intro container is visible)
        if (document.getElementById('introContainer').style.display === 'none') {
            return;
        }
        
        const title = document.getElementById('introTitle');
        const description = document.getElementById('introDescription');
        
        const titleText = 'PsyGen';
        const descText = "A safe space to check in with yourself. I'll ask you some questions about how you've been feeling. This is completely confidential, and there are no right or wrong answers. Just be honest with yourself.";
        
        setTimeout(() => {
            this.typeWriter(title, titleText, 100, () => {
                setTimeout(() => {
                    this.typeWriter(description, descText, 30, () => {
                        setTimeout(() => {
                            this.transitionToChat();
                        }, 2000);
                    });
                }, 500);
            });
        }, 800);
    }
    
    typeWriter(element, text, speed, callback) {
        element.style.opacity = '1';
        element.classList.add('typing-effect');
        let i = 0;
        
        function type() {
            if (i < text.length) {
                element.textContent += text.charAt(i);
                i++;
                setTimeout(type, speed);
            } else {
                element.classList.remove('typing-effect');
                if (callback) callback();
            }
        }
        type();
    }
    
    transitionToChat() {
        this.introContainer.style.opacity = '0';
        this.introContainer.style.transform = 'translateY(-20px)';
        
        setTimeout(() => {
            this.introContainer.style.display = 'none';
            this.chatContainer.classList.add('active');
            this.isIntroComplete = true;
            
            setTimeout(() => {
                this.addBotMessage("Hey there! 💙 I'm Psy, and I'm here to help you understand how you're feeling.");
                setTimeout(() => {
                    this.addBotMessage("Before we start, I want you to know this is a judgment-free zone. Whatever you share stays between us.");
                    setTimeout(() => {
                        this.addBotMessage("I'll ask you about 10 questions. Just type naturally - like you're talking to a friend. No need to overthink it! 😊");
                        setTimeout(() => {
                            this.addBotMessage("Ready? Type 'Psy' to begin, or tell me a bit about yourself first!");
                            this.awaitingResponse = true;
                        }, 2000);
                    }, 2500);
                }, 2500);
            }, 500);
        }, 1000);
    }
    
    sendMessage() {
        if (!this.isIntroComplete || !this.awaitingResponse) return;
        
        const message = this.userInput.value.trim();
        if (!message) return;
        
        this.addUserMessage(message);
        this.userInput.value = '';
        this.awaitingResponse = false;
        
        if (!this.conversationStarted) {
            this.handleIntroResponse(message);
        } else {
            this.handleQuestionResponse(message);
        }
    }
    
    handleIntroResponse(message) {
        const lowerMsg = message.toLowerCase();
        
        if (lowerMsg.includes('psy') || lowerMsg.includes('ready') || lowerMsg.includes('yes') || lowerMsg.includes('start')) {
            setTimeout(() => {
                this.addBotMessage("Awesome! Let's begin. Remember - be 100% honest with yourself. Don't try to sound 'better' or 'worse' than you feel. This is for YOU. 💪");
                setTimeout(() => {
                    this.addBotMessage("Here's a quick heads up: I'll be asking about your feelings, sleep, energy, and thoughts. Just respond naturally in your own words.");
                    setTimeout(() => {
                        this.addBotMessage("One more thing - I'll play some calming music in the background. Take your time with each question. 🎵");
                        setTimeout(() => {
                            this.playBackgroundMusic();
                            this.conversationStarted = true;
                            this.askNextQuestion();
                        }, 2500);
                    }, 2500);
                }, 2500);
            }, 1000);
        } else {
            setTimeout(() => {
                this.addBotMessage(`Nice to meet you! I appreciate you opening up. 💙`);
                setTimeout(() => {
                    this.addBotMessage("Whenever you're ready, just type 'Psy' and we'll get started! 😊");
                    this.awaitingResponse = true;
                }, 2000);
            }, 1000);
        }
    }
    
    playBackgroundMusic() {
        this.bgMusic.volume = 0.3;
        this.bgMusic.play().catch(e => console.log('Music autoplay blocked'));
    }
    
    askNextQuestion() {
        if (this.currentQuestion >= this.questions.length) {
            this.finishAssessment();
            return;
        }
        
        const question = this.questions[this.currentQuestion];
        const progress = `(${this.currentQuestion + 1}/10)`;
        
        setTimeout(() => {
            this.addBotMessage(`${progress} ${question.text}`);
            this.awaitingResponse = true;
        }, 1500);
    }
    
    async handleQuestionResponse(message) {
        this.responses.push(message);
        
        const score = await this.scoreResponse(message, this.questions[this.currentQuestion]);
        this.scores.push(score);
        
        if (this.currentQuestion === 9 && score >= 2) {
            setTimeout(() => {
                this.showCrisisResources();
                setTimeout(() => {
                    this.currentQuestion++;
                    this.askNextQuestion();
                }, 8000);
            }, 1000);
        } else {
            setTimeout(() => {
                this.currentQuestion++;
                this.askNextQuestion();
            }, 800);
        }
    }
    
    showCrisisResources() {
        this.addBotMessage("I want you to know that you're not alone, and there are people who care and want to help.");
        setTimeout(() => {
            this.addBotMessage("If you're having thoughts of hurting yourself, please reach out:");
            setTimeout(() => {
                this.addBotMessage("🆘 National Suicide Prevention Lifeline: 988 (US)\\n💬 Crisis Text Line: Text HOME to 741741\\n🌍 International: https://findahelpline.com");
                setTimeout(() => {
                    this.addBotMessage("These services are free, confidential, and available 24/7. You deserve support. 💙");
                }, 2000);
            }, 2000);
        }, 1500);
    }
    
    async scoreResponse(response, question) {
        try {
            const result = await fetch('/api/score-response', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    response: response,
                    question: question.text,
                    category: question.category
                })
            });
            
            const data = await result.json();
            return data.score;
        } catch (error) {
            console.error('Scoring error:', error);
            return 1;
        }
    }
    
    async finishAssessment() {
        setTimeout(() => {
            this.addBotMessage("Thank you so much for being honest with me. You did great! 🌟");
            setTimeout(async () => {
                this.addBotMessage("Give me a moment while I analyze your responses...");
                
                const totalScore = this.scores.reduce((a, b) => a + b, 0);
                const analysis = await this.getAnalysis(totalScore, this.responses);
                
                setTimeout(() => {
                    this.bgMusic.pause();
                    localStorage.setItem('psygenResult', JSON.stringify({
                        totalScore: totalScore,
                        analysis: analysis,
                        responses: this.responses,
                        scores: this.scores
                    }));
                    window.location.href = 'psygen-results.html';
                }, 3000);
            }, 2000);
        }, 1000);
    }
    
    async getAnalysis(score, responses) {
        try {
            const result = await fetch('/api/analyze-depression', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    total_score: score,
                    responses: responses
                })
            });
            
            return await result.json();
        } catch (error) {
            console.error('Analysis error:', error);
            return this.getDefaultAnalysis(score);
        }
    }
    
    getDefaultAnalysis(score) {
        if (score <= 10) {
            return {
                level: "Minimal",
                message: "You're doing well!",
                recommendations: ["Keep up your self-care routine", "Stay connected with loved ones"]
            };
        } else if (score <= 15) {
            return {
                level: "Mild",
                message: "You might be experiencing some stress.",
                recommendations: ["Try relaxation techniques", "Maintain a regular sleep schedule"]
            };
        } else if (score <= 20) {
            return {
                level: "Moderate",
                message: "It seems like you're going through a challenging time.",
                recommendations: ["Consider talking to someone you trust", "Engage in activities you enjoy"]
            };
        } else {
            return {
                level: "Significant",
                message: "You're dealing with a lot right now.",
                recommendations: ["Please consider reaching out to a mental health professional", "You don't have to go through this alone"]
            };
        }
    }
    
    addUserMessage(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message user';
        messageDiv.innerHTML = `<div class="message-content">${message}</div>`;
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    addBotMessage(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message bot';
        messageDiv.innerHTML = `
            <div class="bot-avatar">
                <img src="https://www.dropbox.com/scl/fi/8s80stxfd9n2zmayneqv6/Screenshot-2025-10-13-044146_imgupscaler.ai_General_4K-Photoroom.png?rlkey=8acaenj6w66ki3qf3nheu29jo&st=obyzuf3x&raw=1" alt="Psy">
            </div>
            <div class="message-content">${message}</div>
        `;
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.psyGenInstance = new PsyGenAssessment();
});
