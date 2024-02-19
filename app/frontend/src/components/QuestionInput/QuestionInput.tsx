import { SetStateAction, useEffect, useState } from "react";
import { useMsal } from "@azure/msal-react";
import { Stack, TextField } from "@fluentui/react";
import { Button, Tooltip, Field, Textarea } from "@fluentui/react-components";
import { Mic28Filled, Send28Filled } from "@fluentui/react-icons";
import { isLoggedIn, requireAccessControl } from "../../authConfig";

import styles from "./QuestionInput.module.css";

interface Props {
    onSend: (question: string) => void;
    disabled: boolean;
    initQuestion?: string;
    placeholder?: string;
    clearOnSend?: boolean;
}

var recognition: {
    continuous: boolean;
    lang: string;
    interimResults: boolean;
    maxAlternatives: number;
    start: () => void;
    onresult: (event: { results: { transcript: SetStateAction<string> }[][] }) => void;
    onend: () => void;
    stop: () => void;
} | null = null;
const SpeechRecognition = (window as any).speechRecognition || (window as any).webkitSpeechRecognition;
try {
    recognition = new SpeechRecognition();
    if (recognition != null) {
        recognition.continuous = true;
        recognition.lang = "en-US";
        recognition.interimResults = true;
        recognition.maxAlternatives = 1;
    }
} catch (err) {
    console.log("SpeechRecognition not supported");
    recognition = null;
}

export const QuestionInput = ({ onSend, disabled, placeholder, clearOnSend, initQuestion }: Props) => {
    const [question, setQuestion] = useState<string>("");
    const [isRecording, setIsRecording] = useState<boolean>(false);

    useEffect(() => {
        initQuestion && setQuestion(initQuestion);
    }, [initQuestion]);

    const sendQuestion = () => {
        if (disabled || !question.trim()) {
            return;
        }

        onSend(question);

        if (clearOnSend) {
            setQuestion("");
        }
    };

    const onEnterPress = (ev: React.KeyboardEvent<Element>) => {
        if (ev.key === "Enter" && !ev.shiftKey) {
            ev.preventDefault();
            sendQuestion();
        }
    };

    const onQuestionChange = (_ev: React.FormEvent<HTMLInputElement | HTMLTextAreaElement>, newValue?: string) => {
        if (!newValue) {
            setQuestion("");
        } else if (newValue.length <= 1000) {
            setQuestion(newValue);
        }
    };

    const { instance } = useMsal();
    const disableRequiredAccessControl = requireAccessControl && !isLoggedIn(instance);

    const startRecording = () => {
        if (recognition == null) {
            console.log("SpeechRecognition not supported");
            return;
        }
        console.log("start recording");
        setIsRecording(true);
        recognition.start();
        recognition.onresult = (event: { results: { transcript: SetStateAction<string> }[][] }) => {
            setQuestion(event.results[0][0].transcript);
            setIsRecording(false);
        };
        recognition.onend = () => {
            setIsRecording(false);
        };
    };

    const stopRecording = () => {
        if (recognition == null) {
            console.log("SpeechRecognition not supported");
            return;
        }
        console.log("stop recording");
        recognition.stop();
        setIsRecording(false);
    };

    const sendQuestionDisabled = disabled || !question.trim() || disableRequiredAccessControl;

    if (disableRequiredAccessControl) {
        placeholder = "Please login to continue...";
    }

    return (
        <Stack horizontal className={styles.questionInputContainer}>
            <TextField
                className={styles.questionInputTextArea}
                disabled={disableRequiredAccessControl}
                placeholder={placeholder}
                multiline
                resizable={false}
                borderless
                value={question}
                onChange={onQuestionChange}
                onKeyDown={onEnterPress}
            />
            <div className={styles.questionInputButtonsContainer}>
                <Tooltip content="Ask question button" relationship="label">
                    <Button size="large" icon={<Send28Filled primaryFill="rgba(115, 118, 225, 1)" />} disabled={sendQuestionDisabled} onClick={sendQuestion} />
                </Tooltip>
            </div>
            {!isRecording && (
                <div className={styles.questionInputButtonsContainer}>
                    <div className={`${styles.questionAudioInputSendButton}`} aria-label="Ask question button" onClick={startRecording}>
                        <Mic28Filled primaryFill="rgba(115, 118, 225, 1)" />
                    </div>
                </div>
            )}
            {isRecording && (
                <div className={styles.questionInputButtonsContainer}>
                    <div className={`${styles.questionAudioInputSendButton}`} aria-label="Ask question button" onClick={stopRecording}>
                        <Mic28Filled primaryFill="rgba(250, 0, 0, 0.7)" />
                    </div>
                </div>
            )}
        </Stack>
    );
};
