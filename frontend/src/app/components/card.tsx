type BinType = 'recyclable' | 'compostable' | 'hazardous' | 'general' | 'unknown';

interface BinDetail {
	src: string;
	alt: string;
	title: string;
	message: string;
}

export default function Card({ binType = "general" }: { binType?: BinType }) {
	const binDetail: Record<BinType, BinDetail> = {
		recyclable: {
			src: "/images/recycleable.png",
			alt: "Recyclable Bin",
			title: "Recyclable Bin",
			message: "Place in yellow bin",
		},
		compostable: {
			src: "/images/compostable.png",
			alt: "Compostable Bin",
			title: "Compostable Bin",
			message: "Place in green bin",
		},
		hazardous: {
			src: "/images/hazardous.png",
			alt: "Hazardous Bin",
			title: "Hazardous Bin",
			message: "Place in red bin",
		},
		general: {
			src: "/images/general.png",
			alt: "General Bin",
			title: "General Bin",
			message: "Place in blue bin",
		},
		unknown: {
			src: "/images/unknown.png",
			alt: "Unknown",
			title: "Cannot Detects Object",
			message: "This bin type is unknown.",
		},
	};

	const { src, alt, title, message } =
		binDetail[binType] || binDetail.general;

	return (
		<div className="h-25 mx-10 bg-white rounded-xl shadow-lg flex items-center gap-x-4">
			<div className="shrink-0 mx-6">
				<img
					className="size-6 m-3"
					src={src}
					alt={alt}
					style={{
						width: "40px",
						height: "80px",
						objectFit: "cover",
						objectPosition: "center",
					}}
				/>
			</div>
			<div className="mr-10">
				<div className="text-xl font-medium text-black">{title}</div>
				<p className="text-slate-500">{message}</p>
			</div>
		</div>
	);
}
