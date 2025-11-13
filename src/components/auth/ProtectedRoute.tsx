
import { ReactNode } from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "@/components/integration/useAuth";

interface ProtectedRouteProps {
  children: ReactNode;
}

const ProtectedRoute = ({ children }: ProtectedRouteProps) => {
  // Временно отключаем проверку подключения магазина для демонстрации
  return <>{children}</>;
};

export default ProtectedRoute;
