"use client";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardAction,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { FcGoogle } from "react-icons/fc";
import { FaGithub } from "react-icons/fa";



export default function LoginPage() {
  const router = useRouter();
  // Redirect to signup page if user want to register first.
  function redirectToSignUpPage() {
    router.push("/auth/signup");
  }
  return (
    <Card className="w-full max-w-md shadow-lg">
      <CardHeader>
        <CardTitle className="text-4xl font-extrabold text-center mb-2">Login</CardTitle>
        <CardDescription className="text-center">
          Authentication credential are required
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form>
          <div className="flex flex-col gap-6">
            <div className="grid gap-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="m@example.com"
                required
              />
            </div>
            <div className="grid gap-2">
              <div className="flex items-center">
                <Label htmlFor="password">Password</Label>
                <Link
                  href="#"
                  className="ml-auto inline-block text-sm underline-offset-4 hover:underline"
                >
                  Forgot your password?
                </Link>
              </div>
              <Input id="password" type="password" required />
            </div>
          </div>
        </form>
      </CardContent>
      <CardFooter className="flex-col gap-2">
        <Button type="submit" className="w-full cursor-pointer">
          Login
        </Button>
        <CardAction>
          <Button className="cursor-pointer text-black dark:text-white" onClick={redirectToSignUpPage} variant="link">Create your account?</Button>
        </CardAction>
        <Button variant="outline" className="w-full cursor-pointer">
          <FcGoogle className="relative right-2 size-5" />Login with Google
        </Button>
        <Button variant="outline" className="w-full cursor-pointer">
          <FaGithub className="relative right-2 size-5" />Login with Github
        </Button>
      </CardFooter>
    </Card>
  );
}
