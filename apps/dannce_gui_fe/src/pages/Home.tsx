import { Link } from 'react-router-dom';

import { Button } from '@/components/ui/button';
import { homePages } from '@/routes';

export default function Root() {
  return (
    <div className="flex flex-col items-center justify-center h-screen">
      <h1 className="scroll-m-20 text-4xl font-extrabold tracking-tight lg:text-5xl mb-5">
        DANNCE Gui
      </h1>
      <div className="flex flex-col gap-4 items-center">
        {homePages.map(({ path, title }) => (
          <Link key={path} to={path}>
            <Button>{title}</Button>
          </Link>
        ))}
      </div>
    </div>
  );
}
