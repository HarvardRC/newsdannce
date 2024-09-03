import { Link } from "react-router-dom";

import { Button } from "@/components/ui/button";

export default function Root() {
  return (
    <div className="flex flex-col items-center justify-center h-screen">
      <h1 className="scroll-m-20 text-4xl font-extrabold tracking-tight lg:text-5xl mb-5"> DANNCE Gui</h1>
      <div className="flex flex-col gap-4 items-center"> {/* Added 'items-center' class */}
        <Link to={"/create-training-dir"}>
          <Button>
            Create Training Directory
          </Button>
        </Link>
        <Link to={"/submit-job"}>
          <Button>
            Submit a job
          </Button>
        </Link>
        <Link to={"/monitor-jobs"}>
          <Button >
            Monitor jobs
          </Button>
        </Link>
      </div>
    </div>
  );
}
