import { initializeApp } from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js';
import { getAuth, signInWithPopup, GoogleAuthProvider, signInWithEmailAndPassword } from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js';

const firebaseConfig = {
    apiKey: "AIzaSyBCJQUtCC7M9bKC936EmfmMpd4_BvQOOyo",
    authDomain: "psy-ec2a6.firebaseapp.com",
    projectId: "psy-ec2a6",
    storageBucket: "psy-ec2a6.firebasestorage.app",
    messagingSenderId: "330888428865",
    appId: "1:330888428865:web:fe615cb979914e3e9cb5c0",
    measurementId: "G-P2W04D0FXW"
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const provider = new GoogleAuthProvider();

window.addEventListener('load', () => {
    document.getElementById('googleSignIn').addEventListener('click', async () => {
        try {
            const result = await signInWithPopup(auth, provider);
            console.log('User signed in:', result.user);
            window.location.href = 'dashboard.html';
        } catch (error) {
            console.error('Error:', error);
            alert('Sign in failed: ' + error.message);
        }
    });
});

document.getElementById('emailForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = e.target[0].value;
    const password = e.target[1].value;
    
    try {
        const result = await signInWithEmailAndPassword(auth, email, password);
        console.log('User signed in:', result.user);
        window.location.href = 'dashboard.html';
    } catch (error) {
        console.error('Error:', error);
        alert('Sign in failed: ' + error.message);
    }
});
