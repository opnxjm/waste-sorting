// "use client";

// import { useState, useEffect, useRef } from "react";
// import Card from "./components/card";

// type BinType = 'recyclable' | 'compostable' | 'hazardous' | 'general' | 'unknown';

// export default function Home() {
//   const [detectedBin, setDetectedBin] = useState<BinType>("unknown");
//   const [isVideoReady, setIsVideoReady] = useState(false); 
//   const videoRef = useRef<HTMLVideoElement | null>(null);

//   useEffect(() => {
//     // Display the video feed
//     if (videoRef.current) {
//       videoRef.current.src = "http://127.0.0.1:5001/video_feed";
//       videoRef.current.oncanplay = () => setIsVideoReady(true); 
//     }

//     // Fetch bin type periodically
//     const intervalId = setInterval(async () => {
//       try {
//         const response = await fetch("http://127.0.0.1:5001/detected_bin", {
//           method: "GET",
//           headers: { "Content-Type": "application/json" },
//         });
//         if (!response.ok) {
//           throw new Error(`HTTP error! Status: ${response.status}`);
//         }
  
//         const data = await response.json();
//         setDetectedBin(data.bin_type);
//         console.log("Detected bin type:", data.bin_type);
//       } catch (error) {
//         console.error("Error fetching detected bin:", error);
//         setDetectedBin("unknown");
//       }
//     }, 1000);
  
//     return () => clearInterval(intervalId);
//   }, []);

//   return (
//     <div className="h-screen relative overflow-hidden">
//       <main className="h-full">
//         <div className="fixed top-0 text-center bg-gray-100 p-4 w-full z-10">
//           <h1 className="text-2xl font-bold">Trash Sorting</h1>
//         </div>
//         <div className="w-screen h-screen bg-gray-200">
//           <video
//             ref={videoRef}
//             autoPlay
//             playsInline
//             crossOrigin="anonymous"
//             style={{ width: "100vw", height: "100%", objectFit: "cover" }}
//           />
//           {!isVideoReady && <div>Loading video feed...</div>} 
//         </div>
//         <div className="fixed bottom-10 w-full flex justify-center">
//           <Card binType={detectedBin} />
//         </div>
//       </main>
//     </div>
//   );
// }


"use client";
// import { useState, useEffect } from "react";
// import Card from "./components/card";

// type BinType = 'recyclable' | 'compostable' | 'hazardous' | 'general' | 'unknown';

// export default function Home() {
//   const [detectedBin, setDetectedBin] = useState<BinType>("unknown");

//   useEffect(() => {
//     // Fetch bin type periodically
//     const intervalId = setInterval(async () => {
//       try {
//         const response = await fetch("http://127.0.0.1:5001/detected_bin", {
//           method: "GET",
//           headers: { "Content-Type": "application/json" },
//         });
//         if (!response.ok) {
//           throw new Error(`HTTP error! Status: ${response.status}`);
//         }

//         const data = await response.json();
//         setDetectedBin(data.bin_type);
//         console.log("Detected bin type:", data.bin_type);
//       } catch (error) {
//         console.error("Error fetching detected bin:", error);
//         setDetectedBin("unknown");
//       }
//     }, 1000);

//     return () => clearInterval(intervalId);
//   }, []);

//   return (
//     <div className="h-screen relative overflow-hidden">
//       <main className="h-full">
//         <div className="fixed top-0 text-center bg-gray-100 p-4 w-full z-10">
//           <h1 className="text-2xl font-bold">Trash Sorting</h1>
//         </div>
//         <div className="w-screen h-screen bg-gray-200">
//           <img
//             src="http://127.0.0.1:5001/video_feed"
//             alt="Video Stream"
//             style={{ width: "100vw", height: "100vh", objectFit: "cover" }}
//           />
//         </div>
//         <div className="fixed bottom-10 w-full flex justify-center">
//           <Card binType={detectedBin} />
//         </div>
//       </main>
//     </div>
//   );
// }

import { useState, useEffect, useRef } from "react";
import io, { Socket } from "socket.io-client";
import Card from "./components/card";
type BinType = 'recyclable' | 'compostable' | 'hazardous' | 'general' | 'unknown';

export default function Home() {
  const [detectedBin, setDetectedBin] = useState<BinType>("unknown");
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const socketRef = useRef<Socket | null>(null);

  useEffect(() => {
    // Connect to WebSocket server
    socketRef.current = io("http://127.0.0.1:5001");
    socketRef.current.on("connect", () => {
      console.log("Connected to WebSocket server");
    });
  
    socketRef.current.on("connect_error", (err) => {
      console.log("WebSocket connection failed: ", err);
    });
  
    // Listen for video frames
    socketRef.current.on("video_frame", (frameData: ArrayBuffer) => {
      // Ensure that frame data is received correctly
      console.log("Received frame data", frameData);

      // Convert frame data to Blob and create a URL
      const arrayBufferView = new Uint8Array(frameData);
      const blob = new Blob([arrayBufferView], { type: "image/jpeg" });
      const url = URL.createObjectURL(blob);

      // Set video source as the received frame
      if (videoRef.current) {
        videoRef.current.src = url;
        videoRef.current.load(); 
        console.log("Set video source to", url);
      }
    });

    // Fetch detected bin type periodically
    const intervalId = setInterval(async () => {
      try {
        const response = await fetch("http://127.0.0.1:5001/detected_bin", {
          method: "GET",
          headers: { "Content-Type": "application/json" },
        });
        const data = await response.json();
        setDetectedBin(data.bin_type);
      } catch (error) {
        console.error("Error fetching detected bin:", error);
      }
    }, 1000);

    return () => {
      clearInterval(intervalId);
      socketRef.current?.disconnect();
    };
  }, []);

  return (
    <><div className="w-screen h-screen bg-gray-200">
      <video
        ref={videoRef}
        autoPlay
        playsInline
        style={{
          width: "100vw",
          height: "100vh",
          objectFit: "cover",
          backgroundColor: "black",
        }} />
    </div><div className="fixed bottom-10 w-full flex justify-center">
        <Card binType={detectedBin} />
      </div></>
  );
}
