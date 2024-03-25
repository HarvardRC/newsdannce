// ask for a file to be imported
fileName = File.openDialog("Select the file to import");
allText = File.openAsString(fileName);
tmp = split(fileName,".");
// get file format {txt, csv}
posix = tmp[lengthOf(tmp)-1];
// parse text by lines
text = split(allText, "\n");


// open second file
fileName2 = File.openDialog("Select the file to import");
allText2 = File.openAsString(fileName2);
tmp2 = split(fileName2,".");
posix2 = tmp2[lengthOf(tmp2)-1];
text2 = split(allText2, "\n");


// define array for points
var xpoints = newArray;
var ypoints = newArray; 

var xpoints2 = newArray;
var ypoints2 = newArray; 

// assume both files are same type? hopefully?

print("importing CSV point set 1...");
//these are the column indexes
hdr = split(text[0]);
iLabel = 0; iX = 1; iY = 2;
// loading and parsing each line
for (i = 1; i < (text.length); i++){
	line = split(text[i],",");
	setOption("ExpandableArrays", true);   
	xpoints[i-1] = parseInt(line[iX]);
	ypoints[i-1] = parseInt(line[iY]);
	print("[1]p("+i+") ["+xpoints[i-1]+"; "+ypoints[i-1]+"]"); 
} 

print("importing CSV point set 2...");
//these are the column indexes
hdr2 = split(text2[0]);
iLabel = 0; iX = 1; iY = 2;
// loading and parsing each line
for (i = 1; i < (text2.length); i++){
	line2 = split(text2[i],",");
	setOption("ExpandableArrays", true);   
	xpoints2[i-1] = parseInt(line2[iX]);
	ypoints2ß[i-1] = parseInt(line2[iY]);
	print("[2]p("+i+") ["+xpoints2[i-1]+"; "+ypoints2[i-1]+"]"); 
} 

// show the points in the image
makeSelection("point small red cross", xpoints, ypoints); 
//makeSelection("point small blue cross", xpoints2, ypoints2); 
