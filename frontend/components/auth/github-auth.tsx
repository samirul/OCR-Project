import { useGitHubLogin } from '@react-oauth/github';
import axios, { AxiosResponse } from 'axios';

const GithubLoginAuth = () => {
  return useGitHubLogin({
    clientId: `${process.env.NEXT_PUBLIC_GITHUB_CLIENT_ID}`,
    redirectUri: 'http://localhost:3000/',
    onSuccess: async response => {
        const res: AxiosResponse = await axios.post(
          `${process.env.NEXT_PUBLIC_GITHUB_API_LOGIN_URL}`, //Google auth backend url.
          { code: response.code }, //Sending google auth code in the backend after successful login from google.
          {
            withCredentials: true, //Http only cookies.
            headers: {
              "Content-Type": "application/json",
            },
          },
        );
        console.log(res)
    },
    onError: error => {
      console.error('Authentication failed:', error);
    },
  });
}

export default GithubLoginAuth;