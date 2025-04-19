// firebaseConfig.js
import { initializeApp } from "firebase/app";
import { getFirestore } from "firebase/firestore";
import { getAuth } from "firebase/auth";
const firebaseConfig = {
    apiKey: "AIzaSyBeDrZ2N47OCG9A-CDqUX7w95cKunrCAEk",
    authDomain: "green-jeddah-7d763.firebaseapp.com",
    databaseURL: "https://green-jeddah-7d763-default-rtdb.firebaseio.com",
    projectId: "green-jeddah-7d763",
    storageBucket: "green-jeddah-7d763.firebasestorage.app",
    messagingSenderId: "995219870604",
    appId: "1:995219870604:web:904290d235a8df69d3bca9"
  };
const app = initializeApp(firebaseConfig);
const db = getFirestore(app);
const auth = getAuth(app);
export { db , auth };
