import { buttonVariants } from "@/components/ui/button";
import { ArrowLeft } from "lucide-react";
import Link from "next/link";
import { ReactNode } from "react";
import { GoogleOAuthProvider } from "@react-oauth/google";

export default function AuthLayout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="absolute top-5 left-5">
        <Link href="/" className={buttonVariants({ variant: "secondary" })}>
          <ArrowLeft className="size-5 relative right-2" />
          Go back
        </Link>
      </div>
      <GoogleOAuthProvider clientId={process.env.NEXT_GOOGLE_CLIENT_ID!}>
        <div className="w-full max-w-md mx-auto">{children}</div>
      </GoogleOAuthProvider>
    </div>
  );
}
