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
import { Controller, useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { signupSchema } from "@/app/schemas/auth";
import { useRouter } from "next/navigation";
import { FcGoogle } from "react-icons/fc";
import { FaGithub } from "react-icons/fa";

export default function SignUpPage() {
  const router = useRouter();
  // Redirect to login page if already registered.
  function redirectToLoginPage() {
    router.push("/auth/login");
  }
  const form = useForm({
    resolver: zodResolver(signupSchema),
    defaultValues: {
      email: "",
      password: "",
      confirmPassword: "",
    },
  });

  function onSubmit() {
    console.log("login success");
  }
  return (
    <Card className="w-full max-w-md shadow-lg lg:mt-0 md:mt-0 mt-20">
      <CardHeader>
        <CardTitle className="text-4xl font-extrabold text-center mb-2">
          Signup
        </CardTitle>
        <CardDescription className="text-center">
          Register your account with credentials
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
              <div className="grid gap-2">
                <div className="flex items-center">
                  <Label htmlFor="password">Confirm password</Label>
                </div>
                <Controller
                  name="confirmPassword"
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
              Register
            </Button>
          </FieldGroup>
        </form>
      </CardContent>
      <CardFooter className="flex-col gap-2">
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
          <FcGoogle className="relative right-2 size-5" />
          Login with Google
        </Button>
        <Button variant="outline" className="w-full cursor-pointer">
          <FaGithub className="relative right-2 size-5" />
          Login with Github
        </Button>
      </CardFooter>
    </Card>
  );
}
