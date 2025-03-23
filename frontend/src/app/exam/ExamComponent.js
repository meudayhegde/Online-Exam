"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

export default function ExamComponent() {
  const [questions, setQuestions] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState({});
  const [timeLeft, setTimeLeft] = useState(30 * 60); // 30 min timer
  const [error, setError] = useState(null); 
  const router = useRouter();

  useEffect(() => {
    const session_id = localStorage.getItem("session_id");

    if (!session_id) {
      router.push("/unauthorized");
      return;
    }

    fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/questions?session_id=${session_id}`)
      .then((res) => res.json())
      .then((data) => {
        console.log(data);
        if (data.questions) {
          setTimeLeft(data.remaining_time)
          setQuestions(data.questions);
        } else {
          setError("Failed to load questions.");
        }
      })
      .catch(() => setError("Error fetching data."));
  }, []);

  const submitExam = () =>{
    let submission = {
      session_id: localStorage.getItem("session_id"),
      answers: Object.keys(selectedAnswers).map(key=> {return {'question_id': key, 'choice': selectedAnswers[key]}})
    }
    console.log(submission);
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/submit`, {
        method: 'POST',
        headers:{
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(submission)
    })
    .then((res) => res.json())
    .then((data) => {
        if(data.status === 'complete'){
            router.push('/complete')
        }
    })
    .catch(() => setError("Error Submitting exxam"));
  }

  useEffect(() => {
    if (timeLeft <= 0) {
      submitExam()
      return
    };
    const timer = setInterval(() => setTimeLeft((prev) => prev - 1), 1000);
    return () => clearInterval(timer);
  }, [timeLeft]);

  if (error) return <p className="text-red-500">{error}</p>;
  if (!questions.length) return <p>Loading questions...</p>;

  const currentQuestion = questions[currentIndex];

  const handleAnswerSelection = (choice) => {
    setSelectedAnswers((prev) => ({ ...prev, [currentQuestion._id]: choice }));
  };

  const handleNavigation = (index) => {
    setCurrentIndex(index);
  };

  const handleNext = () => {
    if (currentIndex < questions.length - 1) {
      setCurrentIndex((prev) => prev + 1);
    }else if(currentIndex === questions.length - 1){
      submitExam()
    }
  };

  const handlePrev = () => {
    if (currentIndex > 0) {
      setCurrentIndex((prev) => prev - 1);
    }
  };

  const getHr = (sec) => Math.floor(sec / (60 * 60))
  const getMn = (sec) => Math.floor(sec / 60) % 60
  const getSc = (sec) => sec % 60

  return (
    <div className="h-screen flex flex-col items-center justify-center bg-gray-100">
      {/* Question Navigation */}
      <div className="flex flex-wrap gap-2 justify-center mb-4 absolute top-4">
          {questions.map((q, index) => (
            <button
              key={q._id}
              className={`w-8 h-8 rounded-full ${
                index === currentIndex ? "bg-blue-500 text-white" : (selectedAnswers[q._id] !== undefined ? "bg-green-500 text-white" : "bg-gray-300")
              }`}
              onClick={() => handleNavigation(index)}
            >
              {index + 1}
            </button>
          ))}
        </div>

      {/* Timer */}
      <div className={"absolute top-4 right-4 text-white py-2 px-3 rounded-xl " + ((timeLeft < 15)? "bg-red-500": "bg-green-500")}>
        Time Left: {getHr(timeLeft) < 10 ? "0" : ""}{getHr(timeLeft)}:{getMn(timeLeft) < 10 ? "0" : ""}{getMn(timeLeft)}:{getSc(timeLeft) < 10 ? "0" : ""}{getSc(timeLeft)}
      </div>

      {/* Exam Container */}
      <div className="bg-white p-6 rounded-lg shadow-md w-[600px]">
        <h2 className="text-xl font-bold text-center mb-4">{currentQuestion.subject_name}</h2>

        {/* Current Question */}
        <p className="font-semibold mb-2">{currentQuestion.question}</p>
        {currentQuestion.image && (
          <img src={currentQuestion.image} alt="Question" className="mb-4" />
        )}

        {/* Answer Choices */}
        <div className="space-y-2">
          {currentQuestion.choices.map((choice, idx) => (
            <label key={idx} className="block">
              <input
                type="radio"
                name={`question-${currentQuestion._id}`}
                value={choice}
                checked={selectedAnswers[currentQuestion._id] === idx}
                onChange={() => handleAnswerSelection(idx)}
                className="mr-2"
              />
              {choice}
            </label>
          ))}
        </div>

        {/* Navigation Buttons */}
        <div className="flex justify-between mt-4">
          <button
            onClick={handlePrev}
            disabled={currentIndex === 0}
            className="bg-gray-500 text-white px-4 py-2 rounded disabled:opacity-50"
          >
            Prev
          </button>
          <button
            onClick={handleNext}
            className={((currentIndex === questions.length - 1)? "bg-green-500 ":"bg-blue-500 ") + "text-white px-4 py-2 rounded"}
          >
            {(currentIndex === questions.length - 1) ? "Submit" : "Next"}
          </button>
        </div>
      </div>
    </div>
  );
}