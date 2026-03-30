import { OAuthResponse, useGitHubLogin } from "@react-oauth/github";
import axios, { AxiosResponse } from "axios";
import { useRouter } from "next/navigation";

// Interface for axios response.
interface AuthResponse {
  access_token: string;
  user: {
    email: string;
    id: number | string;
  };
}

const GithubLoginAuth = () => {
  const router = useRouter();
  return useGitHubLogin({
    clientId: `${process.env.NEXT_PUBLIC_GITHUB_CLIENT_ID}`,
    redirectUri: "http://localhost:3000/",
    onSuccess: async (codeResponse: OAuthResponse) => {
      try {
        const response: AxiosResponse<AuthResponse> = await axios.post(
          `${process.env.NEXT_PUBLIC_GITHUB_API_LOGIN_URL}`, //Github auth backend url.
          { code: codeResponse.code }, //Sending github auth code in the backend after successful login from github.
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
          response.data?.access_token &&
          response.data?.user?.id
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
    onError: (error) => {
      console.error("Authentication failed:", error);
      router.push("/auth/login"); //Redirect to login page.
    },
  });
};

export default GithubLoginAuth;
