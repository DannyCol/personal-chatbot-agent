// App.tsx
import { useEffect, useState,  } from 'react';
import { initializeApp } from "firebase/app";
import { getAuth, GoogleAuthProvider, signInWithPopup, onAuthStateChanged, User } from "firebase/auth";
import ChatbotMessenger from './App.tsx'
import { UserContext } from './contexts.ts'
import { firebaseConfig } from './firebaseConfig.ts';  // injected using github secrets

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const provider = new GoogleAuthProvider();
provider.setCustomParameters({
  prompt: "select_account",
});

const AuthFirst = () => {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
      setUser(currentUser);
    });
    return () => unsubscribe();
  }, []);

  const handleGoogleSignIn = async () => {
    await signInWithPopup(auth, provider);
  };
  return (
    <UserContext.Provider value={user}>
      {user ?
        <> 
          Welcome, {user.displayName}! <ChatbotMessenger />
        </> :
        <>
          <button onClick={handleGoogleSignIn}>Sign in with Google</button>
        </>
      }
    </UserContext.Provider>
    
  )
};

export default AuthFirst;
