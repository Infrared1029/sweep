'use client'
import { usePostHog } from 'posthog-js/react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from './ui/card';
import { Input } from "./ui/input"
import { Label } from './ui/label'
import { Button } from './ui/button';
import { Textarea } from './ui/textarea';
import { useEffect, useState } from 'react';

export default function Feedback({
    onClose
}: {
    onClose: () => void
}) {
    const posthog = usePostHog();
    const [feedback, setFeedback] = useState("")
    const surveyID = process.env.NEXT_PUBLIC_SURVEY_ID

    useEffect(() => {
        posthog.capture("survey shown", {
            $survey_id: surveyID // required
        })
    }, [posthog])


    const handleSurveyDismissed = (e: any) => {
        e.preventDefault();
        posthog.capture("survey dismissed", {
            $survey_id: surveyID,
        });
        localStorage.setItem(`hasInteractedWithSurvey_${surveyID}`, 'true');
        onClose();
    }

    const handleFeedbackSubmit = (e: any) => {
        e.preventDefault();
        console.log(feedback)
        posthog.capture("survey sent", {
            $survey_id: surveyID,
            $survey_response: feedback
        });
        localStorage.setItem(`hasInteractedWithSurvey_${surveyID}`, 'true');
        onClose();
    }

    return (
        <Card className="w-[500px] fixed right-4 bottom-4">
            <CardHeader>
                <CardTitle>Give us Feedback</CardTitle>
                <CardDescription>Sweep Chat is new so we&apos;re actively trying to improve it for developers like you.</CardDescription>
            </CardHeader>
            <CardContent>
                <form>
                    <div className="grid w-full items-center gap-4">
                        <div className="flex flex-col space-y-1.5">
                            <Label htmlFor="feedback">How can we improve Sweep Chat for you?</Label>
                            <Textarea
                                id="feedback"
                                value={feedback}
                                onChange={(e) => setFeedback(e.target.value!)}
                                placeholder="E.g. I would like to upload images to Sweep Chat."
                            />
                        </div>
                    </div>
                </form>
            </CardContent>
            <CardFooter className="flex justify-between">
                <Button variant="outline" onClick={handleSurveyDismissed}>Cancel</Button>
                <Button onClick={handleFeedbackSubmit}>Submit</Button>
            </CardFooter>
        </Card>
    );
}