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
import {
  Field,
  FieldError,
  FieldGroup,
  FieldLabel,
} from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import Link from "next/link";
import { Controller, useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { loginSchema } from "@/app/schemas/auth";
import GoogleLoginAuth from '@/components/auth/google-auth';
import GithubLoginAuth from "@/components/auth/github-auth";
import { useRouter } from "next/navigation";
import { FcGoogle } from "react-icons/fc";
import { FaGithub } from "react-icons/fa";

export default function LoginPage() {
  const router = useRouter();
  // Redirect to signup page if user want to register first.
  function redirectToSignUpPage() {
    router.push("/auth/signup");
  }
  const form = useForm({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: "",
      password: "",
    },
  });

  function onSubmit() {
    console.log("login success");
  }
  //Get login function for google login.
  const { login } = GoogleLoginAuth();
  const {initiateGitHubLogin, isLoading} = GithubLoginAuth();

  return (
    <Card className="w-full max-w-md shadow-lg lg:mt-0 md:mt-0 mt-14">
      <CardHeader>
        <CardTitle className="text-4xl font-extrabold text-center mb-2">
          Login
        </CardTitle>
        <CardDescription className="text-center">
          Authentication credential are required
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={form.handleSubmit(onSubmit)}>
          <FieldGroup className="gap-y-4">
            <div className="flex flex-col gap-5">
              <div className="grid gap-2">
                <Controller
                  name="email"
                  control={form.control}
                  render={({ field, fieldState }) => (
                    <Field>
                      <FieldLabel>Email</FieldLabel>
                      <Input
                        aria-invalid={fieldState.invalid}
                        placeholder="john@doe.com"
                        {...field}
                      />
                      {fieldState.invalid && (
                        <FieldError errors={[fieldState.error]} />
                      )}
                    </Field>
                  )}
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
                <Controller
                  name="password"
                  control={form.control}
                  render={({ field, fieldState }) => (
                    <Field>
                      <Input
                        aria-invalid={fieldState.invalid}
                        placeholder=""
                        type="password"
                        {...field}
                      />
                      {fieldState.invalid && (
                        <FieldError errors={[fieldState.error]} />
                      )}
                    </Field>
                  )}
                />
              </div>
            </div>
            <Button type="submit" className="w-full cursor-pointer">
              Login
            </Button>
          </FieldGroup>
        </form>
      </CardContent>
      <CardFooter className="flex-col gap-2">
        <CardAction>
          <Button
            className="cursor-pointer text-black dark:text-white"
            onClick={redirectToSignUpPage}
            variant="link"
          >
            Create your account?
          </Button>
        </CardAction>
          <Button variant="outline" className="w-full cursor-pointer" onClick={login}>
          <FcGoogle className="relative right-2 size-5" />
          Login with Google
        </Button>
        <Button variant="outline" className="w-full cursor-pointer" onClick={initiateGitHubLogin} disabled={isLoading}>
          <FaGithub className="relative right-2 size-5" />
          Login with Github
        </Button>
      </CardFooter>
    </Card>
  );
}
