import { createContext } from "react";
import { User } from 'firebase/auth';

export const UserContext = createContext<User | null>(null);