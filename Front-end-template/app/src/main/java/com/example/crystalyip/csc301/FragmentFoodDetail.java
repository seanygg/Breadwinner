package com.example.crystalyip.csc301;

import android.app.AlertDialog;
import android.graphics.drawable.ColorDrawable;
import android.os.AsyncTask;
import android.os.Bundle;
import android.os.StrictMode;
import android.support.annotation.NonNull;
import android.support.annotation.Nullable;
import android.support.constraint.ConstraintLayout;
import android.support.design.widget.FloatingActionButton;
import android.support.v4.app.Fragment;
import android.text.SpannableString;
import android.text.style.RelativeSizeSpan;
import android.view.Gravity;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.PopupWindow;
import android.widget.TextView;

import com.example.crystalyip.csc301.HTTPInteractions.HTTPRequests;
import com.example.crystalyip.csc301.HTTPInteractions.OrderPlacer;
import com.example.crystalyip.csc301.Model.Listing;
import com.example.crystalyip.csc301.Model.Order;
import com.example.crystalyip.csc301.Model.StaticStorage;

import java.io.IOException;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.Scanner;

public class FragmentFoodDetail extends Fragment  implements View.OnClickListener{

    private View rootView;
    private Order orderToPlace;
    private int cookID;
    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        rootView =inflater.inflate(R.layout.fragment_food_detail, container, false);
        Bundle bundle = this.getArguments();

        Button button = rootView.findViewById(R.id.btnViewProfileFromFood);
        button.setOnClickListener(new View.OnClickListener() {
            public void onClick(View v) {
                openProfile(v);
            }
        });


        if (bundle != null) {
            Listing listing = bundle.getParcelable("Listing");
            ImageView imageView=rootView.findViewById(R.id.image_food);
            imageView.setImageBitmap(listing.getImageBytes());

            TextView tv = rootView.findViewById(R.id.food_description);
            String foodName = listing.getFoodName();
            String foodLocation = listing.getLocation();
            double foodPrice=listing.getPrice();
            int listindID=listing.getListingID();
            String foodDescription="$"+foodPrice+" "+foodName+"\n"+foodLocation;
            SpannableString descriptions = new SpannableString(foodDescription);
            descriptions.setSpan(new RelativeSizeSpan(1.3f), 0, foodDescription.indexOf("\n"), 0);
            tv.setText(descriptions);
            cookID=listing.getCookID();
            orderToPlace = new Order("Pending", listindID, StaticStorage.getUserId(), foodName, foodLocation);

        }

        FloatingActionButton order=rootView.findViewById(R.id.btnCart);
        order.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {

                AlertDialog.Builder builder = new AlertDialog.Builder(getActivity());
                builder.setCancelable(true);
                try {
                    builder.setMessage(getSuccessResponse(orderToPlace));
                    AlertDialog alertDialog = builder.create();
                    alertDialog.show();
                    alertDialog.getWindow().setLayout(800, 400);
                    alertDialog.getWindow().setBackgroundDrawableResource(R.drawable.panels);
                    sendOrderNotification();
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
        });
        return rootView;
    }

    private void sendOrderNotification(){
        System.out.println("running1");
        AsyncTask.execute(new Runnable() {
            @Override
            public void run() {
                System.out.println("running2");
                int SDK_INT = android.os.Build.VERSION.SDK_INT;
                if (SDK_INT > 8) {
                    StrictMode.ThreadPolicy policy = new StrictMode.ThreadPolicy.Builder()
                            .permitAll().build();
                    StrictMode.setThreadPolicy(policy);
                    String notificationRecipient = "";

                    //This is a Simple Logic to Send Notification different Device Programmatically....
                    notificationRecipient=Integer.toString(cookID);
                    /*
                    if (MainActivity.userId.equals("12")) { //TODO: Use the order's notification ID
                        notificationRecipient = "12";
                    }*/
                    HTTPRequests.sendOneSignalMessage(notificationRecipient);

                }
            }
        });
    }

    private String getSuccessResponse(Order orderToPlace) throws IOException {
        OrderPlacer orderPlacer=new OrderPlacer(orderToPlace);
        String res = orderPlacer.makeOrder();
        if (res.toLowerCase().equals("success"))
            return "Your order has been successfully placed";
        return "Order has not been placed. " +
                "You may have too many pending orders or the listing has been closed.";
    }

    public void openProfile(View view) {
        ProfileFragment pf =new ProfileFragment();
        Bundle bundy = new Bundle();
        bundy.putInt("CookID", cookID);
        pf.setArguments(bundy);
        getFragmentManager().beginTransaction().replace(R.id.fragment_container,
                pf).commit();

    }

    @Override
    public void onClick(View v) {
    }
}
