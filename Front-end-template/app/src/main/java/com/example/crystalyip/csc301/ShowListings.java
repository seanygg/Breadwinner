package com.example.crystalyip.csc301;

import android.annotation.SuppressLint;
import android.graphics.Color;
import android.os.Bundle;
import android.os.StrictMode;
import android.support.v4.app.Fragment;
import android.support.v4.app.FragmentTransaction;
import android.support.v4.widget.SwipeRefreshLayout;
import android.text.SpannableString;
import android.text.style.ForegroundColorSpan;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.AdapterView;
import android.widget.ImageView;
import android.widget.ListView;
import android.widget.SimpleAdapter;


import com.example.crystalyip.csc301.DAOs.ListingsDAO;
import com.example.crystalyip.csc301.HTTPInteractions.HTTPRequests;
import com.example.crystalyip.csc301.Model.CustomAdapter;
import com.example.crystalyip.csc301.Model.Listing;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;

import org.json.JSONArray;
import org.json.JSONObject;

public class ShowListings extends Fragment implements View.OnClickListener {

    public static String searchURL;/* = "http://18.234.123.109/api/getAllListings";*/
    private View view;
    /**
     * This "constructor" sets the searchURL to display every listing.
     */
    public ShowListings() {
        searchURL = "http://18.234.123.109/api/getAllListings";
    }

    /**
     * This "constructor" sets the searchURL to search for listings matching the query.
     */
    @SuppressLint("ValidFragment")
    public ShowListings(String query) {
        String formattedQuery = query.replace("\\s", "+");
        searchURL = "http://18.234.123.109/api/search/" + formattedQuery;
    }



    /**
     * Create the "Near me" view
     */
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) {
        // reference: https://www.viralandroid.com/2016/02/android-listview-with-image-and-text.html
        StrictMode.ThreadPolicy policy = new StrictMode.ThreadPolicy.Builder().permitAll().build();
        StrictMode.setThreadPolicy(policy);

        // Inflate the layout for this fragment
        view = inflater.inflate(R.layout.fragment_show_listings, container, false);
        refreshListings();
        final SwipeRefreshLayout pullToRefresh = view.findViewById(R.id.swipe_layout);
        pullToRefresh.setOnRefreshListener(new SwipeRefreshLayout.OnRefreshListener() {
            @Override
            public void onRefresh() {
                refreshListings();
                pullToRefresh.setRefreshing(false);
            }
        });
        return view;
    }

    public void refreshListings(){
        ListingsDAO listingsDAO = new ListingsDAO(searchURL);
        final List<Listing> populatedListings = listingsDAO.getAllListings();

        List<HashMap<String, Object>> aList = new ArrayList<>();
        List<Listing> finalListings=new ArrayList<>();
        for (int i = 0; i < populatedListings.size(); i++) {
            if (populatedListings.get(i).isStatus()){
                HashMap<String, Object> titleImagePair = new HashMap<>();
                String foodDetail = populatedListings.get(i).getFoodName() + "\n  " + populatedListings.get(i).getLocation();
                SpannableString spannable = new SpannableString("  $" + populatedListings.get(i).getPrice() + " " + foodDetail);
                spannable.setSpan(new ForegroundColorSpan(Color.RED), 0, foodDetail.indexOf("\n"), 0);
                aList.add(titleImagePair);
                finalListings.add(populatedListings.get(i));
            }

        }

        CustomAdapter simpleAdapter = new CustomAdapter(getActivity(), (ArrayList<Listing>) finalListings);


        final ListView listingsList = view.findViewById(R.id.lstFoodList);
        listingsList.setClickable(true);
        listingsList.setAdapter(simpleAdapter);
        listingsList.setOnItemClickListener(new AdapterView.OnItemClickListener() {

            @Override
            public void onItemClick(AdapterView<?> parent, View view, int position, long id) {
                Bundle bundle = new Bundle();

                bundle.putParcelable("Listing", populatedListings.get(position));
                FragmentFoodDetail foodDetail = new FragmentFoodDetail();
                foodDetail.setArguments(bundle);
                FragmentTransaction ft = getFragmentManager().beginTransaction();

                ft.replace(R.id.fragment_container,
                        foodDetail);
                ft.addToBackStack(null);
                ft.commit();
                // id and position refer to the index of the clicked thing
                System.out.println("Clicked the item at position " + position + ". ID is " + id);
            }
        });
    }

    @Override
    public void onClick(View v) {

    }
}