import z from 'zod';

export const loginSchema = z.object({
    email: z.email(),
    password: z.string().min(8).max(30),
})

export const signupSchema = z.object({
    email: z.email(),
    password: z.string().min(8).max(30),
    confirmPassword: z.string().min(8).max(30)
})