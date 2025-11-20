import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { authActions } from "@/actions/auth";
import { ROUTES } from "@/config";
import Spinner from "../Spinner";

interface ProtectedRouteProps {
  children: React.ReactNode;
  requireAuth?: boolean;
  redirectTo?: string;
}

export default function ProtectedRoute({
  children,
  requireAuth = true,
  redirectTo
}: ProtectedRouteProps) {
  const navigate = useNavigate();
  const [isChecking, setIsChecking] = useState(true);
  const [isAuthorized, setIsAuthorized] = useState(false);

  useEffect(() => {
    const checkAuth = async () => {
      const isAuth = await authActions.verifyAuth();

      if (requireAuth && !isAuth) {
        // Need auth but not logged in → redirect to login
        navigate(redirectTo || ROUTES.LOGIN);
      } else if (!requireAuth && isAuth) {
        // Don't need auth but logged in → redirect to dashboard
        navigate(redirectTo || ROUTES.LINEUP_CONSTRUCTOR);
      } else {
        // All good, show the page
        setIsAuthorized(true);
      }

      setIsChecking(false);
    };

    checkAuth();
  }, [navigate, requireAuth, redirectTo]);

  if (isChecking) {
    return <Spinner />;
  }

  return isAuthorized ? <>{children}</> : null;
}
