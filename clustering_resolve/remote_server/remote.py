from fastapi import FastAPI
import uvicorn
import PetexRoutines as PE
import subprocess

app = FastAPI()

resolve_file="test_resolve.rsl"


@app.get("/open_resolve")
def open_resolve():

    o = subprocess.Popen(r'C:\Program Files\Petroleum Experts\IPM 12.5\resolve.exe')

    return {"message": "Resolve application started up!"}



@app.get("/open_resolve_file")
def open_resolve_file():

    osID=PE.InitializeID()
    PEserver=PE.Initialize(osID["id"],osID["comId"])
    PE.DoCmd(PEserver,"Resolve.OPENFILE('" + resolve_file + "')")
    PE.Stop(PEserver)

    return {"message": "Resolve file opened!"}



@app.get("/run")
def run():
    print("got it")

    osID=PE.InitializeID()
    PEserver=PE.Initialize(osID["id"],osID["comId"])
    PE.DoCmd(PEserver,"Resolve.RUN()")
    PE.Stop(PEserver)

    return {"message": "Resolve running!"}


@app.get("/check_status")
def check_status():

    osID=PE.InitializeID()
    PEserver=PE.Initialize(osID["id"],osID["comId"])

    status=int(PE.DoGet(PEserver,"Resolve.PubVar[{status}].Value"))

    if status==1:
        status="running"
    else:
        status="not active"

    PE.Stop(PEserver)

    return {"status": status}



@app.get("/get_forecast_data")
def get_forecast_data():

    osID=PE.InitializeID()
    PEserver=PE.Initialize(osID["id"],osID["comId"])
    
    status=int(PE.DoGet(PEserver,"Resolve.PubVar[{status}].Value"))
    
    results=[]

    if status==0:
        for row in range(1000):
            try:
                r={}
                os_val=PE.DoGet(PEserver,"Resolve.Module[{GAP}].Results[{CurrentRun}][{Sep1}]["+str(row)+"].Time")
                r["date"]=(float(os_val))
                os_val=PE.DoGet(PEserver,"Resolve.Module[{GAP}].Results[{CurrentRun}][{Sep1}]["+str(row)+"].OilRate#Sm3/day")
                r["qoil"]=(float(os_val))
                os_val=PE.DoGet(PEserver,"Resolve.Module[{GAP}].Results[{CurrentRun}][{Sep1}]["+str(row)+"].GasRate#1000Sm3/d")
                r["qgas"]=(float(os_val))
                # os_val=PE.DoGet(PEserver,"Resolve.Module[{GAP}].Results[{CurrentRun}][{Sep1}]["+str(row)+"].OilRate#Sm3/day")
                r["qwater"]=(float(0))
                results.append(r)
            except:
                break

    PE.Stop(PEserver)

    return {
        "status":status,
        "results":results
    }


if __name__ == "__main__":
    uvicorn.run("remote:app", host="127.0.0.1", port=3000, reload=True)