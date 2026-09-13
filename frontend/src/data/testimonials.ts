export interface Testimonial {
  name: string;
  role: string;
  quote: string;
  score?: string;
}

export const TESTIMONIALS: Testimonial[] = [
  {
    name: "Chiamaka O.",
    role: "JAMB candidate, Lagos",
    quote: "The AI tutor explained limits better than three YouTube videos combined — and it showed me exactly which textbook page it came from.",
    score: "312 UTME score",
  },
  {
    name: "Tobenna A.",
    role: "300L Medicine, UNILAG",
    quote: "I used it to revise Biochemistry before my MB BS exams. Being able to expand the citation and check the actual textbook line saved me so much doubt.",
  },
  {
    name: "Fatima B.",
    role: "WAEC candidate, Kano",
    quote: "My free mock exams got me hooked. Now my whole class uses it before Further Maths tests.",
    score: "A1 in Further Maths",
  },
  {
    name: "Engr. David S.",
    role: "200L Mechanical Engineering, FUTA",
    quote: "Static and dynamics problems finally make sense when the tutor walks through the LaTeX step by step instead of just giving an answer.",
  },
  {
    name: "Blessing N.",
    role: "HND Accounting, Yaba College of Technology",
    quote: "The mock CBT format is identical to what we sit for in the exam hall. No surprises on exam day anymore.",
  },
  {
    name: "Mrs. Adeyemi",
    role: "Parent, Guardian plan",
    quote: "The weekly report tells me exactly which subjects my three kids are struggling with — I don't have to guess anymore.",
  },
];
