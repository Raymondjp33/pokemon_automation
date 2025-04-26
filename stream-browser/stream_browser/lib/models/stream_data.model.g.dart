// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'stream_data.model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

StreamData _$StreamDataFromJson(Map<String, dynamic> json) => StreamData(
      switch1CurrentlyHunting: json['switch1_currently_hunting'] as String,
      switch2CurrentlyHunting: json['switch2_currently_hunting'] as String,
      away: json['away'] as bool,
      streamStarttime: json['stream_starttime'] as num,
      switch1GifNumber: json['switch1_gif_number'] as String,
      switch2GifNumber: json['switch2_gif_number'] as String,
    );

Map<String, dynamic> _$StreamDataToJson(StreamData instance) =>
    <String, dynamic>{
      'switch1_currently_hunting': instance.switch1CurrentlyHunting,
      'switch2_currently_hunting': instance.switch2CurrentlyHunting,
      'away': instance.away,
      'stream_starttime': instance.streamStarttime,
      'switch1_gif_number': instance.switch1GifNumber,
      'switch2_gif_number': instance.switch2GifNumber,
    };
