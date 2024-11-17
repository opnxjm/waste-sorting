"use client";

import { useState, useRef, useEffect } from "react";
import Card from "./components/card"

export default function Home() {
	const [showCamera, setShowCamera] = useState(false);
	const videoRef = useRef<HTMLVideoElement | null>(null);

	const openCamera = async () => {
		setShowCamera(true);
		if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
			try {
				const stream = await navigator.mediaDevices.getUserMedia({
					video: { facingMode: "environment" },
				});
				if (videoRef.current) {
					videoRef.current.srcObject = stream;
				}
			} catch (error) {console.error("Error accessing camera:", error);
			}
		}
	};

	useEffect(() => {
		openCamera();
	}, []); // Empty dependency array means this runs once when the component mounts

	return (
		<div className="h-screen font-[family-name:var(--font-geist-sans)] relative overflow-hidden">
			<main className="h-full">
				{/* Sticky Header */}
				<div className="fixed top-0 text-center bg-gray-100 p-4 sm:p-6 w-full z-10 flex items-center justify-center">
					<h1 className="text-xl sm:text-2xl font-bold text-black">
						Trash Sorting
					</h1>
				</div>

				{/* Video Section */}
				<div className="w-screen h-screen bg-green-500">
					{showCamera && (
						<div className="relative w-screen h-screen">
							<video
								ref={videoRef}
								autoPlay
								playsInline
								style={{
									width: "100vw",
									height: "100%",
									objectFit: "cover",
								}}
							></video>
						</div>
					)}
				</div>

				{/* Sticky Card at the bottom */}
				<div
					className="fixed bottom-10 w-full p-4 sm:p-6 flex justify-center"
					style={{ paddingBottom: "env(safe-area-inset-bottom)" }} // Tailwind doesn't have a utility for safe-area-inset
				>
					<Card />
				</div>
			</main>
		</div>
	);



}