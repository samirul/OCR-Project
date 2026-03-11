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

export default function SignUpPage() {
  const router = useRouter();
  // Redirect to login page if already registered.
  function redirectToLoginPage() {
    router.push("/auth/login");
  }
  return (
    <Card className="w-full max-w-md shadow-lg">
      <CardHeader>
        <CardTitle className="text-4xl font-extrabold text-center mb-2">
          Signup
        </CardTitle>
        <CardDescription className="text-center">
          Register your account with credentials
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
              </div>
              <Input id="password" type="password" required />
            </div>
            <div className="grid gap-2">
              <div className="flex items-center">
                <Label htmlFor="password">Confirm password</Label>
              </div>
              <Input id="password" type="password" required />
            </div>
          </div>
        </form>
      </CardContent>
      <CardFooter className="flex-col gap-2">
        <Button type="submit" className="w-full cursor-pointer">
          Register
        </Button>
        <CardAction>
          <Button
            className="cursor-pointer text-black dark:text-white"
            onClick={redirectToLoginPage}
            variant="link"
          >
            Already created your account?
          </Button>
        </CardAction>
        <Button variant="outline" className="w-full cursor-pointer">
          Signup with Google
        </Button>
        <Button variant="outline" className="w-full cursor-pointer">
          Signup with Github
        </Button>
      </CardFooter>
    </Card>
  );
}
