import z from 'zod';

export const loginSchema = z.object({
    email: z.email(),
    password: z.string().min(8).max(30),
})

export const signupSchema = z.object({
    username: z.string().max(30),
    email: z.email(),
    password: z.string().min(8).max(30),
    confirmPassword: z.string().min(8).max(30)
})
.superRefine(({username}, ctx)=>{
  if(username === "" || username === null){
     ctx.addIssue({
        code: "custom",
        message: "The username should not be blank",
        path: ['username']
      });
  }
})
.superRefine(({ confirmPassword, password }, ctx) => {
    if (confirmPassword !== password) {
      ctx.addIssue({
        code: "custom",
        message: "The password and confirm password did not match",
        path: ['confirmPassword']
      });
    }
  });