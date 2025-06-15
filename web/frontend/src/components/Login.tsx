import { GoogleAuthProvider, signInWithPopup } from 'firebase/auth';
import { auth } from '../firebase';

const Login: React.FC = () => {
  const handleLogin = async () => {
    const provider = new GoogleAuthProvider();
    try {
      await signInWithPopup(auth, provider);
    } catch (err) {
      console.error('Login failed', err);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <button
        className="bg-blue-600 text-white px-4 py-2 rounded-lg"
        onClick={handleLogin}
      >
        Sign in with Google
      </button>
    </div>
  );
};

export default Login;
