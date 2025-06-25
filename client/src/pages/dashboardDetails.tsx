import React, { Fragment, useEffect, useState } from "react";
import { Link, useParams, useLocation } from "react-router";

import Button from "@mui/joy/Button";
import Typography from "@mui/joy/Typography";
import InfoOutlined from "@mui/icons-material/InfoOutlined";
import Table from "@mui/joy/Table";
import Sheet from "@mui/joy/Sheet";
import Input from "@mui/joy/Input";
import Box from "@mui/joy/Box";
import Card from "@mui/joy/Card";
import CardContent from "@mui/joy/CardContent";
import KeyboardArrowDown from '@mui/icons-material/KeyboardArrowDown';

import Select, { selectClasses } from '@mui/joy/Select';
import Option from '@mui/joy/Option';
import Divider from '@mui/joy/Divider';

const DASHBOARD_COPY_API_ENDPOINT = "http://localhost:5000/api/v1/copy_dashboard";
const DATASET_API_ENDPOINT = "http://localhost:5000/api/v1/datasets"


function DashboardDetails() {
  const params = useParams();
  const dashboardId: number = Number(params.id);

  const { state } = useLocation();
  const { dashboardTitle } = state;

  // React hooks
  const [datasetList, setDatasetList] = useState([]); 
  //const [dataset, setDataset] = useState(""); 
  const [sourceDashboardTitle, setSourceDashboardTitle] = useState(dashboardTitle);
  const [newDashboardId, setNewDashboardId] = useState("");
  const [newDashboardTitle, setNewDashboardTitle] = useState("");

  const [sliceConfigMap, setSliceConfigMap] = useState([] as any);

  const [editRowId, setEditRowId] = useState(null);
  const [editedData, setEditedData] = useState({}); // Stores changes for the currently edited row

    const getDatasets = async () => {
  
  const datasetGetResponse = await fetch(DATASET_API_ENDPOINT, {
    method: 'GET',
    headers: {
      'Accept': 'application/json'
    }
  })
  const datasetData = await datasetGetResponse.json();
  let datasetListing: any = [];
    datasetData.forEach(function (item: any) {
      let newObject: any = {
        dataset_id: item.id,
        dataset: item.table_name,
        datasource_type: item.datasource_type,
        modified: item.changed_on_delta_humanized,
        database_id: item.database.id,
        database_name: item.database.database_name,
        schema: item.schema,
        explore_url: item.explore_url
      };
      datasetListing.push(newObject);
    });

  if (!datasetListing) {
    console.warn("Dataset listing missing from response. Check if the Superset API has been changed.");   
  }
  setDatasetList(datasetListing)

return datasetGetResponse;
}

const onCloneDashboard = async (
    dashboardId: number,
    newDashboardTitle: string
  ) => {
    const payload = {
      dashboard_id: dashboardId,
      new_dashboard_title: newDashboardTitle,
    };

    const response = await fetch(DASHBOARD_COPY_API_ENDPOINT, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });
    // Parse the JSON response
    const dashboardInfo = await response.json();
    const newDashboardId = dashboardInfo["result"]["id"]; 
    setNewDashboardId(newDashboardId)
    //console.info("#".repeat(10))

    onLoadChartDetails(newDashboardId);
  };

  const onLoadChartDetails = async (dashboardId: number) => {
    const FETCH_CHART_DETAILS_ENDPOINT = `http://localhost:5000/api/v1/load_slice_details`;
    const payload = {
      dashboard_id: dashboardId,
    };

    const response = await fetch(FETCH_CHART_DETAILS_ENDPOINT, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    // Parse the JSON response
    const sliceInfoData = await response.json();

    // Method 1: Using filter to get table_name from datasetList array object
    let matchingEntriesFilter = datasetList.filter(item1 =>
      sliceInfoData.some(item2 => item1.dataset_id === Number(item2.dataset))
    );

    const updatedSliceInfoData = sliceInfoData.map(slice => ({
      ...slice, // Copy all existing properties
      dataset_name: matchingEntriesFilter[0].dataset || "Unknown dataset" 
    }));

    setSliceConfigMap(sliceInfoData);
    setSliceConfigMap(updatedSliceInfoData);
  };

   const onDatasourceChange = async (rowId: any, newDatasourceValue: any, oldDatasourceValue: any) => {
    const foundDatasource: any = datasetList.find(item => item.dataset === newDatasourceValue);
    const newDatasetId: number = foundDatasource.dataset_id
    const newDatasetName: number = foundDatasource.dataset
    const oldDatasetId: number = oldDatasourceValue

    console.info(foundDatasource)

    setSliceConfigMap(prevSliceConfigMap => {
      return prevSliceConfigMap.map(item => {
        if (item.slice_id === rowId) {
          return { ...item, dataset: newDatasetId, dataset_name: newDatasetName};
        }
        return item;
      });
    });

    const payload = {
      sliceId: rowId,
      newDashboardId: newDashboardId,
      oldDatasetId: oldDatasetId,
      newDatasetId: newDatasetId,
      newDatasetName: newDatasetName
    };

    const UPDATE_CHART_DATASOURCE_ENDPOINT = `http://localhost:5000/api/v1/update_chart_datasource`;

    const response = await fetch(UPDATE_CHART_DATASOURCE_ENDPOINT, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    // Parse the JSON response
    //const data = await response.json();

  };

   const onUpdateChart = async () => {

    const UPDATE_CHART_DETAILS_ENDPOINT = `http://localhost:5000/api/v1/update_charts`;
    const payload = sliceConfigMap;

    const response = await fetch(UPDATE_CHART_DETAILS_ENDPOINT, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    // Parse the JSON response
    const data = await response.json();
    //console.info(data)
    
  };

  const handleEditClick = (rowId: any) => {

    setEditRowId(rowId);

    // Initialize editedData with the current row's data
    setEditedData(sliceConfigMap.find((item) => item.slice_id === rowId));
  };

  const handleSaveClick = (rowId) => {
    setSliceConfigMap((prevSliceConfigMap) =>
      prevSliceConfigMap.map((item) =>
        item.slice_id === rowId ? { ...item, ...editedData } : item
      )
    );

    onUpdateChart();

    setEditRowId(null); // Exit edit mode
    setEditedData({}); // Clear edited data

    
  };

  const handleCancelClick = () => {
    setEditRowId(null); // Exit edit mode
    setEditedData({}); // Clear edited data
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setEditedData((prev) => ({ ...prev, [name]: value }));
  };

  const arrayDatasetItems = datasetList?.map(({dataset_id, dataset}: any) => 
    <Option key={dataset_id} value={dataset}>{dataset}</Option> 
 )

  useEffect(() => {
    getDatasets();
    onUpdateChart();
    
  }, [DATASET_API_ENDPOINT, sliceConfigMap, editRowId]);

  return (
    <Fragment>
      <Box
        sx={{
          width: "100%",
          //maxWidth: '70%',
          mx: "auto",
          mt: 4,
        }}
      >
        <Card variant="outlined">
          <CardContent>
            <Typography
              startDecorator={<InfoOutlined />}
              //level="h2"
              level="body-lg"
              sx={{ fontSize: "xl", mb: 0.5, color: "#004687" }}
            >
              Source Dashboard: {sourceDashboardTitle}
            </Typography>
          </CardContent>
        </Card>

        <p style={{ paddingTop: 5 }}>
          <Input
            sx={{ "--Input-decoratorChildHeight": "45px" }}
            placeholder="Destination dashboard name"
            onChange={(e: any) => setNewDashboardTitle(e.target.value)}
            required
            variant="outlined"
            size="sm"
            //value={newDashboardTitle}
            endDecorator={
              <Button
                //loading
                variant="solid"
                color="primary"
                sx={{ borderTopLeftRadius: 0, borderBottomLeftRadius: 0 }}
                onClick={() => onCloneDashboard(dashboardId, newDashboardTitle)}
              >
                Clone Dashboard
              </Button>
            }
          />
        </p>
      </Box>

      <Box
        sx={{
          width: "100%",
          //maxWidth: '80%',
          mx: "auto",
          mt: 4,
        }}
      >
        <Card variant="outlined">
          <CardContent>
            <div style={{ padding: "20px" }}>
              <Sheet variant="plain" sx={{ pt: 1, borderRadius: "sm" }}>
                <p>
                  <Typography
                    startDecorator={<InfoOutlined />}
                    level="h2"
                    sx={{ fontSize: "xl", mb: 0.5 }}
                  >
                    New Dashboard Title: {newDashboardTitle}
                  </Typography>
                </p>

                {/*  <p>
         <Button
        size="sm"
        style={{ margin: "20px" }}
        onClick={() => onLoadChartDetails(dashboardId)}
      >
        Load Charts
      </Button>
     </p>
      */}
                <Table aria-label="basic table">
                  <caption>A list of related charts</caption>
                  <thead>
                    <tr>
                      <th style={{ width: "10%" }}>Source ID</th>
                      <th>Source chart</th>
                      <th>Destination chart</th>
                      <th>Dataset</th> 
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {sliceConfigMap.map((item) => (
                      <tr key={item.slice_id}>
                        <td>{item.slice_id}</td>
                        {editRowId === item.slice_id ? (
                          <>
                            <td>
                              <input
                                disabled
                                type="text"
                                name="sourceChart"
                                value={editedData.sourceChart || ""}
                                onChange={handleChange}
                              />
                            </td>
                            <td>
                              <input
                                type="text"
                                name="destinationChart"
                                value={editedData.destinationChart || ""}
                                onChange={handleChange}
                              />
                            </td>
                            
                             <td>
                             <Box 
                             //sx={{ width: 270 }}
                             >
                                <Select
                                  defaultValue={editedData.dataset_name}
                                  placeholder="Choose dataset…" 
                                  onChange={(e: any, newValue) => onDatasourceChange(item.slice_id, newValue, item.dataset )}
                                  slotProps={{
                                    listbox: {
                                      placement: 'bottom-start',
                                      sx: { minWidth: 160 },
                                    },
                                  }}
                                  indicator={<KeyboardArrowDown />}
                                  sx={{
                                  //width: 240,
                                    [`& .${selectClasses.indicator}`]: {
                                      transition: '0.2s',
                                      [`&.${selectClasses.expanded}`]: {
                                        transform: 'rotate(-180deg)',
                                      },
                                    },
                                  }}
                                  size="md">
                                  {arrayDatasetItems}
                                </Select> 
                  </Box>
                            </td> 
                          </>
                        ) : (
                          <>
                            <td>{item.sourceChart}</td>
                            <td>{item.destinationChart}</td>
                               <td>
                                <Select 
                                  disabled
                                  defaultValue={item.dataset_name} 
                                  placeholder="Choose dataset…" 
                                  size="sm"
                                >
                                {datasetList?.map(({dataset_id, dataset}: any) => 

                                <div> 
                                      <Divider/>
                                      <Option key={dataset_id} value={dataset}>{dataset}</Option> 
                                      </div>
                                  )}
                              </Select> 
                                </td> 
                          </>
                        )}
                        <td>
                          {editRowId === item.slice_id ? (
                            <>
                              <button
                                onClick={() => handleSaveClick(item.slice_id)}
                              >
                                Save
                              </button>
                              <button
                                onClick={handleCancelClick}
                                style={{ marginLeft: "5px" }}
                              >
                                Cancel
                              </button>
                            </>
                          ) : (
                            <button
                              onClick={() => handleEditClick(item.slice_id)}
                            >
                              Edit
                            </button>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              </Sheet>
            </div>
          </CardContent>
        </Card>
      </Box>
    </Fragment>
  );
}

export default DashboardDetails;
