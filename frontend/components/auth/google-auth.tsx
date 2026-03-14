import axios, { AxiosResponse } from "axios";
import { useGoogleLogin, CodeResponse } from "@react-oauth/google";
import { useRouter } from "next/navigation";

// Interface for axios response.
interface AuthResponse {
  access: string;
  user: {
    pk: number | string;
    email: string;
  };
}

//Authentication with google.
const GoogleLoginAuth = () => {
  const router = useRouter();
  const login = useGoogleLogin({
    onSuccess: async (codeResponse: CodeResponse) => {
      try {
        const response: AxiosResponse<AuthResponse> = await axios.post(
          `${process.env.NEXT_PUBLIC_GOOGLE_API_LOGIN_URL}`, //Google auth backend url.
          { code: codeResponse.code }, //Sending google auth code in the backend after successful login from google.
          {
            withCredentials: true, //Http only cookies.
            headers: {
              "Content-Type": "application/json",
            },
          },
        );
        //Checking if response status code is 200 and can fetch access token and user id.
        if (
          response.status === 200 &&
          response.data?.access &&
          response.data?.user?.pk
        ) {
          router.push("/"); //Redirect user after successful login.
        }
        // If something is wrong or error then redirect to login page.
      } catch (error) {
        if (axios.isAxiosError(error)) {
          const status = error.response?.status; //Get error status code.
          const message = error.response?.data; //Get error messages.

          console.error("Data fetching error:", {
            status,
            message,
          });

          if (status === 400 || status === 401 || status === 500) {
            router.push("/auth/login"); //Redirect to login page.
          }
        } else {
          console.error("Unexpected error redirected to login page:", error);
          router.push("/auth/login"); //Redirect to login page.
        }
      }
    },
    flow: "auth-code",
    onError: (error) => {
      router.push("/auth/login"); //Redirect to login page.
    },
  });

  return { login };
};

export default GoogleLoginAuth;
