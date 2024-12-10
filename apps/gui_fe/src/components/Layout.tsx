import { appPages, headerLinks } from '@/routes';
import { Link, Outlet } from 'react-router-dom';

export default function RootLayout() {
  return (
    <>
      <div className="relative flex min-h-screen flex-col bg-background">
        <header className="top-0 flex h-16 items-center gap-4 border-b bg-background px-4 md:px-6">
          <nav className="hidden flex-row gap-6 text-lg font-medium md:flex md:flex-row md:items-center md:gap-5 md:text-sm lg:gap-6 relative">
            <Link
              to={appPages.root.path}
              className="flex items-center gap-2 text-lg font-semibold md:text-base"
            >
              <span className="">DANNCE GUI</span>
            </Link>
            {headerLinks.map((x) => (
              <Link
                key={x.path}
                to={x.path}
                className="text-muted-foreground transition-colors hover:text-foreground"
              >
                <span className="">{x.title}</span>
              </Link>
            ))}

            <div className="text-muted-foreground transition-colors hover:text-foreground flex-1">
              <div className="flex flex-row justify-end">
                <span className="cursor-pointer">Kill Server [disabled]</span>
              </div>
            </div>
          </nav>
        </header>
        <div className="flex flex-col mx-10 mt-8 gap-4 mb-12">
          <Outlet />
        </div>
      </div>
    </>
  );
}
