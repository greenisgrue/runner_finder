DELETE FROM dbo.Runner;

BULK INSERT dbo.Runner
   FROM 'C:\Users\Simon Wahlström\Documents\Projects\DataScraping\master_files\runner.csv'  
   WITH   
      (  
	     FIRSTROW = 2,
		 CODEPAGE = '65001',
		 DATAFILETYPE = 'widechar',
         FIELDTERMINATOR =',',  
         ROWTERMINATOR ='\n'  
      );
GO