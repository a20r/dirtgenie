import { useEffect, useState } from 'react';
import { auth, db } from '../firebase';
import { doc, getDoc, setDoc } from 'firebase/firestore';
import { signOut } from 'firebase/auth';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => {
  const [openaiKey, setOpenaiKey] = useState('');
  const [googleKey, setGoogleKey] = useState('');
  const user = auth.currentUser;

  useEffect(() => {
    const fetchKeys = async () => {
      if (!user) return;
      const ref = doc(db, 'users', user.uid);
      const snap = await getDoc(ref);
      if (snap.exists()) {
        const data = snap.data() as any;
        if (data.openaiKey) {
          setOpenaiKey(data.openaiKey);
          sessionStorage.setItem('openai_api_key', data.openaiKey);
        }
        if (data.googleMapsKey) {
          setGoogleKey(data.googleMapsKey);
          sessionStorage.setItem('google_maps_api_key', data.googleMapsKey);
        }
      }
    };
    fetchKeys();
  }, [user]);

  const saveKeys = async () => {
    if (!user) return;
    await setDoc(doc(db, 'users', user.uid), {
      openaiKey,
      googleMapsKey: googleKey,
    });
    sessionStorage.setItem('openai_api_key', openaiKey);
    sessionStorage.setItem('google_maps_api_key', googleKey);
    onClose();
  };

  const logout = async () => {
    await signOut(auth);
  };

  return (
    <div
      className={`fixed inset-y-0 left-0 w-64 bg-white shadow-lg transform ${
        isOpen ? 'translate-x-0' : '-translate-x-full'
      } transition-transform`}
    >
      <div className="p-4 border-b flex justify-between items-center">
        <h2 className="font-bold">Settings</h2>
        <button onClick={onClose}>X</button>
      </div>
      <div className="p-4 space-y-4">
        <div>
          <label className="block text-sm">OpenAI Key</label>
          <input
            type="password"
            className="w-full border rounded p-2"
            value={openaiKey}
            onChange={e => setOpenaiKey(e.target.value)}
          />
        </div>
        <div>
          <label className="block text-sm">Google Maps Key</label>
          <input
            type="password"
            className="w-full border rounded p-2"
            value={googleKey}
            onChange={e => setGoogleKey(e.target.value)}
          />
        </div>
        <button
          onClick={saveKeys}
          className="w-full bg-blue-600 text-white py-2 rounded"
        >
          Save
        </button>
        <button
          onClick={logout}
          className="w-full bg-gray-300 py-2 rounded"
        >
          Sign Out
        </button>
      </div>
    </div>
  );
};

export default Sidebar;
