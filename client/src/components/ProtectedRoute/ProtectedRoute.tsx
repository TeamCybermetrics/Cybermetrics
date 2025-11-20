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

/**
 * Protects a route by verifying the user's authentication and conditionally rendering or redirecting.
 *
 * Verifies authentication on mount; while verification is in progress renders a Spinner. If the user
 * is allowed to view the route, renders `children`. If the user must be authenticated but is not,
 * navigates to `redirectTo` or the login route. If authentication is not required but the user is
 * authenticated, navigates to `redirectTo` or the lineup constructor route.
 *
 * @param children - Content to render when the route is permitted
 * @param requireAuth - If true, the route requires an authenticated user; if false, authenticated users will be redirected away
 * @param redirectTo - Optional path to override the default redirect target when a redirect is performed
 * @returns The component's rendered element: a Spinner during auth verification, the `children` when authorized, or `null` after denial (redirects occur when applicable)
 */
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