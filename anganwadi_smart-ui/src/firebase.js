import { initializeApp } from "firebase/app";
import { getFirestore } from "firebase/firestore";
import { getAuth } from "firebase/auth";
import { getStorage } from "firebase/storage";

const firebaseConfig = {
  apiKey: "AIzaSyDGvJUssEbV6kbxx-fV5eHQIj2rTuUzeqQ",
  authDomain: "angawadi-smart.firebaseapp.com",
  projectId: "angawadi-smart",
  storageBucket: "angawadi-smart.firebasestorage.app",
  messagingSenderId: "567724675161",
  appId: "1:567724675161:web:e374401bfef2a5cf082148"
};

const app = initializeApp(firebaseConfig);
export const db = getFirestore(app);
export const auth = getAuth(app);
export const storage = getStorage(app);
export default app;