// Import Firebase scripts
importScripts("https://www.gstatic.com/firebasejs/9.6.7/firebase-app-compat.js");
importScripts("https://www.gstatic.com/firebasejs/9.6.7/firebase-messaging-compat.js");

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyB1kJgiTGAjxDY3cjqlLPNPSY440hHjl-o",
  authDomain: "oasira-oauth.firebaseapp.com",
  projectId: "oasira-oauth",
  storageBucket: "oasira-oauth.firebasestorage.app",
  messagingSenderId: "253107350539",
  appId: "1:253107350539:web:a30b4dc1a87c75e9e9ab0e",
  measurementId: "G-QRG2LLH9XD"
};

// Initialize Firebase
if (!firebase.apps.length) {
    firebase.initializeApp(firebaseConfig);
}

const messaging = firebase.messaging();

messaging.onBackgroundMessage(function(payload) {
  console.log('[firebase-messaging-sw.js] Received background message ', payload);
  
  const notificationTitle = payload.notification.title;
  const notificationOptions = {
    body: payload.notification.body,
    icon: 'https://www.oasira.ai/images/logos/colored-logomark.png'
  };

  // @ts-ignore
  self.registration.showNotification(notificationTitle, notificationOptions);
});
