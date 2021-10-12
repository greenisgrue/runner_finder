DELETE FROM dbo.Race;

BULK INSERT dbo.Race
   FROM 'C:\Users\Simon Wahlström\Documents\Projects\DataScraping\master_files\race.csv'  
   WITH   
      (  
	     FIRSTROW = 2,
		 CODEPAGE = '65001',
		 DATAFILETYPE = 'widechar',
         FIELDTERMINATOR =',',  
         ROWTERMINATOR ='\n'  
      );
GO