"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { authActions } from "@/actions/auth";
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
  const router = useRouter();
  const [isChecking, setIsChecking] = useState(true);
  const [isAuthorized, setIsAuthorized] = useState(false);

  useEffect(() => {
    const checkAuth = async () => {
      const isAuth = await authActions.verifyAuth();

      if (requireAuth && !isAuth) {
        // Need auth but not logged in → redirect to login
        router.push(redirectTo || "/login");
      } else if (!requireAuth && isAuth) {
        // Don't need auth but logged in → redirect to dashboard
        router.push(redirectTo || "/dashboard");
      } else {
        // All good, show the page
        setIsAuthorized(true);
      }

      setIsChecking(false);
    };

    checkAuth();
  }, [router, requireAuth, redirectTo]);

  if (isChecking) {
    return <Spinner />;
  }

  return isAuthorized ? <>{children}</> : null;
}

