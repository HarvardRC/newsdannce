import { forwardRef } from 'react';

import { ControllerRenderProps } from 'react-hook-form';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from './ui/table';
import { Checkbox } from './ui/checkbox';
import { appPages } from '@/routes';
import { Link } from 'react-router-dom';

type CustomProps = {
  options: {
    name: string;
    path: string;
    id: number;
  }[];
  multiSelect: boolean;
  // value: any;
  // onChange: any;
  // onBlur: any;
  // name: string;
} & ControllerRenderProps;

const AddVideoFoldersInput = forwardRef<any, CustomProps>(
  //@ts-ignore
  ({ options, multiSelect = false, ...field }, ref) => {
    // const inputRef = useRef<HTMLInputElement>(null);

    const isRowSelected = (thisRowId: number) => {
      return field.value.includes(thisRowId);
    };

    const toggleRowSelected = (thisRowId: number) => {
      if (multiSelect) {
        if (isRowSelected(thisRowId)) {
          const newArray: [] = field.value.filter(
            (x: number) => x != thisRowId
          );
          field.onChange(newArray);
        } else {
          const newArray = [...field.value, thisRowId];
          newArray.sort();
          field.onChange(newArray);
        }
      } else {
        if (isRowSelected(thisRowId)) {
          // ignore
        } else {
          const newArray = [thisRowId];
          field.onChange(newArray);
        }
      }
    };

    return (
      <>
        <div className="">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-[20px]">-</TableHead>
                {/* <TableHead className="w-[20px]">ID</TableHead> */}
                <TableHead>Name</TableHead>
                <TableHead>Path</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {options!.map((x) => {
                return (
                  <TableRow key={x.id}>
                    <TableCell className="">
                      <Checkbox
                        checked={isRowSelected(x.id)}
                        onClick={() => toggleRowSelected(x.id)}
                      />
                    </TableCell>
                    {/* <TableCell className="font-medium">{x.id}</TableCell> */}
                    <TableCell>
                      <Link
                        to={appPages.videoFolderDetails.path.replace(
                          /:id/,
                          `${x.id}`
                        )}
                        target="_blank"
                      >
                        {x.name}
                      </Link>
                    </TableCell>
                    <TableCell>{x.path}</TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </div>
      </>
    );
  }
);

export default AddVideoFoldersInput;
