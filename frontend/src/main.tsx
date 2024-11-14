import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import AuthFirst from './AuthFirst.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <AuthFirst />
  </StrictMode>,
)
