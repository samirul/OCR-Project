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
import GoogleLoginAuth from "@/components/auth/google-auth";
import GithubLoginAuth from "@/components/auth/github-auth";
import z, { email } from "zod";
import { useEffect, useTransition } from "react";
import { Loader2 } from "lucide-react";
import axios, { AxiosResponse } from "axios";
import { getCookie } from 'cookies-next';
import { toast } from "sonner";

export default function SignUpPage() {
  // loading transition
  const [isPending, startTransition] = useTransition();
  const router = useRouter();
  // Redirect to login page if already registered.
  function redirectToLoginPage() {
    router.push("/auth/login");
  }
  // zod form
  const form = useForm({
    resolver: zodResolver(signupSchema),
    defaultValues: {
      username: "",
      email: "",
      password: "",
      confirmPassword: "",
    },
  });

  // ── Fetch CSRF token when page loads ──
  useEffect(() => {
    const fetchCsrfToken = async () => {
      try {
        await axios.get(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/csrf/new/csrf_token/`, {
          withCredentials: true,
        });
      } catch (error) {
        console.error("Failed to fetch CSRF token:", error);
      }
    };
    fetchCsrfToken();
  }, []);

  function onSubmit(data: z.infer<typeof signupSchema>) {
    startTransition(async () => { // loading animation in submit button
      try{
        const csrf_token = await getCookie('csrf_token'); // fetch csrf token for signup
        // send form data to backend
        const response: AxiosResponse = await axios.post(
          `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/user/auth/register`,
          { email: data.email,
            username: data.username,
            password: data.password,
            confirm_password: data.confirmPassword
          },
          {
            withCredentials: true, // send required token from cookie automatically
            headers: {
              'X-CSRF-Token': csrf_token, // send csrf token
              'Content-Type': 'application/json',
              'Accept': 'application/json',
            },
          }
        );
        toast.success(response?.data.data.msg) // toast success
      }catch(error){
        if (axios.isAxiosError(error)) {
          const status = error.response?.status; //Get error status code.
          const toastError = error.response?.data.errors[0]?.message;
          toast.error(toastError); // toast error
          const message = error.response?.data; //Get error messages.
          // console.error("Data fetching error:", {
          //   status,
          //   message,
          // });
          if (status === 400 || status === 401 || status === 500 || status === 403) {
            router.push("/auth/signup"); //Redirect to register page.
          }
        } else {
          toast.error("Something unexpected happened, redirected to signup page"); // toast error
          // console.error("Unexpected error redirected to signup page:", error);
          router.push("/auth/signup"); //Redirect to register page.
        }
      }
    });
  }
  //Get login function for google login and github login.
  const { login } = GoogleLoginAuth();
  const { initiateGitHubLogin, isLoading } = GithubLoginAuth();

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
                  name="username"
                  control={form.control}
                  render={({ field, fieldState }) => (
                    <Field>
                      <FieldLabel>Username</FieldLabel>
                      <Input
                        aria-invalid={fieldState.invalid}
                        placeholder="JohnDoe"
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
                        placeholder="*********"
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
                        placeholder="*********"
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
            <Button
              type="submit"
              className="w-full cursor-pointer"
              disabled={isPending}
            >
              {isPending ? (
                <>
                  <Loader2 className="size-4 mr-1.5 animate-spin text-white" />
                  <span>Loading...</span>
                </>
              ) : (
                <span>Register</span>
              )}
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
        <Button
          variant="outline"
          className="w-full cursor-pointer"
          onClick={login}
        >
          <FcGoogle className="relative right-2 size-5" />
          Login with Google
        </Button>
        <Button
          variant="outline"
          className="w-full cursor-pointer"
          onClick={initiateGitHubLogin}
          disabled={isLoading}
        >
          <FaGithub className="relative right-2 size-5" />
          Login with Github
        </Button>
      </CardFooter>
    </Card>
  );
}
